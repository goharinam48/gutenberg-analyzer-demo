from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BookIDForm
from .models import Book
from django.contrib import messages
import json
from openai import OpenAI
from django.conf import settings
import requests
client = OpenAI(api_key=settings.OPENAI_API_KEY)
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def fetch_book_data(book_id):
    content_urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt"
    ]
    metadata_url = f"https://www.gutenberg.org/ebooks/{book_id}"
    
    text = None
    for url in content_urls:
        try:
            logger.info(f"Fetching content from {url}")
            content_response = requests.get(url, timeout=10)
            if content_response.status_code == 200:
                text = content_response.text
                break
            else:
                logger.error(f"Content fetch failed with status {content_response.status_code}")
        except RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            continue
    
    if not text:
        logger.error("No valid content URL found")
        return None, None
    
    try:
        logger.info(f"Fetching metadata from {metadata_url}")
        metadata_response = requests.get(metadata_url, timeout=10)
        if metadata_response.status_code != 200:
            logger.error(f"Metadata fetch failed with status {metadata_response.status_code}")
            return None, None
        soup = BeautifulSoup(metadata_response.text, 'html.parser')
        
        metadata_table = soup.find('table', class_='bibrec')
        if not metadata_table:
            logger.error("Metadata table not found")
            return text, {'title': 'Unknown', 'author': 'Unknown'}
        
        title = "Unknown"
        author = "Unknown"
        for row in metadata_table.find_all('tr'):
            th = row.find('th')
            td = row.find('td')
            if th and td:
                header = th.text.strip().lower()
                if 'title' in header:
                    title = td.text.strip()
                elif 'author' in header:
                    author = td.text.strip()
        
        metadata = {'title': title.lower(), 'author': author.lower()}
        logger.info(f"Metadata extracted: {metadata}")
        
        return text, metadata
    except RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return None, None
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
import json

@login_required
def home(request):
    if request.method == 'POST':
        form = BookIDForm(request.POST)
        if form.is_valid():
            book_id = form.cleaned_data['book_id']
            text, metadata = fetch_book_data(book_id)
            if text and metadata:
                logger.info(f"Saving metadata for {book_id}: {metadata}")
                # Use the dict directly, no need for json.dumps
                metadata_dict = {'title': metadata['title'], 'author': metadata['author']}
                book, created = Book.objects.get_or_create(
                    book_id=book_id,
                    defaults={'text': text, 'metadata': metadata_dict}  # Pass dict directly
                )
                if not created:
                    book.text = text
                    book.metadata = metadata_dict  # Pass dict directly
                    book.save()
                book.accessed_by.add(request.user)
                return redirect('book_detail', book_id=book_id)
            else:
                messages.error(request, f"Failed to fetch book data for ID {book_id}.")
                return redirect('home')
    else:
        form = BookIDForm()
    return render(request, 'books/home.html', {'form': form})

import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    # Deserialize the metadata JSON string into a dictionary
    metadata = book.metadata if isinstance(book.metadata, dict) else json.loads(book.metadata)
    context = {
        'book': book,
        'title': metadata.get('title', 'No Title'),
        'author': metadata.get('author', 'Unknown'),
    }
    return render(request, 'books/book_detail.html', context)


@login_required
def accessed_books(request):
    books = request.user.accessed_books.all()
    for book in books:
        book.metadata = book.metadata if isinstance(book.metadata, dict) else json.loads(book.metadata)
    return render(request, 'books/accessed_books.html', {'books': books})

@login_required
def analyze_book(request, book_id, analysis_type):
    book = Book.objects.get(book_id=book_id)
    metadata = book.metadata if isinstance(book.metadata, dict) else json.loads(book.metadata)
    title = metadata.get('title', 'No Title')

    if analysis_type == 'summary':
        prompt = f"Summarize the following book:\n\n{book.text[:4000]}"
    elif analysis_type == 'characters':
        prompt = f"List the main characters in the following book:\n\n{book.text[:4000]}"
    else:
        messages.error(request, "Invalid analysis type.")
        return redirect('book_detail', book_id=book_id)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        analysis_result = response.choices[0].message.content
    except Exception as e:
        messages.error(request, f"Failed to perform analysis: {str(e)}")
        return redirect('book_detail', book_id=book_id)

    return render(request, 'books/analysis_result.html', {
        'book': book,
        'analysis_type': analysis_type,
        'result': analysis_result,
        'title': title  # Pass the title to the template
    })

from django.contrib import admin
from .models import Book
import json
from django.utils.html import format_html
from django.urls import reverse

class BookAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('book_id', 'get_title', 'get_author', 'text_preview')

    # Filters for the sidebar
    list_filter = ('book_id',)

    # Searchable fields
    search_fields = ('book_id', 'metadata__title', 'metadata__author')

    # Make text and metadata fields read-only to prevent accidental edits
    readonly_fields = ('text', 'metadata')

    def get_title(self, obj):
        # Handle metadata as dict or str (for legacy data)
        if isinstance(obj.metadata, str):
            try:
                metadata = json.loads(obj.metadata)
                return metadata.get('title', 'No Title')
            except json.JSONDecodeError:
                return 'Invalid Metadata'
        return obj.metadata.get('title', 'No Title')
    get_title.short_description = 'Title'

    def get_author(self, obj):
        if isinstance(obj.metadata, str):
            try:
                metadata = json.loads(obj.metadata)
                return metadata.get('author', 'Unknown')
            except json.JSONDecodeError:
                return 'Unknown'
        return obj.metadata.get('author', 'Unknown')
    get_author.short_description = 'Author'

    def text_preview(self, obj):
        # Split the text into lines and show the first 5 lines
        lines = obj.text.splitlines()
        preview = ' '.join(lines[:5])
        if len(lines) > 5:
            # Add a "See more" link
            see_more_link = reverse('admin:books_book_change', args=[obj.id])
            return format_html('{}... <a href="{}">See more</a>', preview, see_more_link)
        return preview
    text_preview.short_description = 'Text Preview'

# Register the Book model with the custom admin class
admin.site.register(Book, BookAdmin)

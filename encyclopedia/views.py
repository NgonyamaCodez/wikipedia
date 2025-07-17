from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
import os
import re
import random
import markdown2
from django.utils.html import escape

from . import util


# =============================
# Forms
# =============================

class NewPageForm(forms.Form):
    title = forms.CharField(
        label="Title",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100
    )
    content = forms.CharField(
        label="Content (Markdown)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10})
    )


class EditPageForm(forms.Form):
    title = forms.CharField(
        label="Title",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100
    )
    content = forms.CharField(
        label="Content (Markdown)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10})
    )


# =============================
# Views
# =============================

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' was not found."
        })

    html_content = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })


def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('index')

    entries = util.list_entries()
    exact_matches = [entry for entry in entries if query.lower() == entry.lower()]

    if exact_matches:
        return redirect('entry', title=exact_matches[0])

    substring_matches = [entry for entry in entries if query.lower() in entry.lower()]
    return render(request, "encyclopedia/search_results.html", {
        'query': query,
        'matches': substring_matches
    })


def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries available"
        })

    random_title = random.choice(entries)
    return redirect('entry', title=random_title)


def create(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            entries = util.list_entries()

            if any(title.lower() == e.lower() for e in entries):
                return render(request, "encyclopedia/create.html", {
                    "form": form,
                    "error": f"An entry with the title '{title}' already exists."
                })

            util.save_entry(title, content)
            return redirect("entry", title=title)

    form = NewPageForm(initial={
        'content': util.get_new_entry_template()
    })
    return render(request, "encyclopedia/create.html", {"form": form})


def edit(request, title):
    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            new_title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Prevent duplicate titles
            if new_title != title and util.get_entry(new_title):
                form.add_error('title', f"An entry with the title '{new_title}' already exists.")
                return render(request, "encyclopedia/edit.html", {
                    "original_title": title,
                    "form": form
                })

            # Save updated content
            util.save_entry(new_title, content)

            # Remove old file if title changed
            if new_title != title:
                old_filename = os.path.join("entries", f"{title}.md")
                if os.path.exists(old_filename):
                    os.remove(old_filename)

            return redirect("entry", title=new_title)

    # GET request
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' doesn't exist."
        })

    form = EditPageForm(initial={'title': title, 'content': content})
    return render(request, "encyclopedia/edit.html", {
        "original_title": title,
        "form": form
    })


# =============================
# Optional: Custom Markdown Parser (if needed)
# =============================

def custom_markdown_to_html(markdown):
    markdown = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', markdown)
    markdown = re.sub(r'^- (.*?)$', r'<li>\1</li>', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', markdown, flags=re.DOTALL)
    markdown = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', markdown)

    lines = markdown.split('\n')
    html_lines = []
    in_paragraph = False

    for line in lines:
        if not line.strip():
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            continue

        if not (line.startswith('<') and line.endswith('>')):
            if not in_paragraph:
                html_lines.append('<p>')
                in_paragraph = True
            html_lines.append(line)
        else:
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            html_lines.append(line)

    if in_paragraph:
        html_lines.append('</p>')

    html = '\n'.join(html_lines)
    return escape(html)

        
        
    
        
        
        
        




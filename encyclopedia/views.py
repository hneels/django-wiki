from django.shortcuts import render
from . import util
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
import markdown
import random

# new entry form for New template
class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    newentry = forms.CharField(widget=forms.Textarea, label="New Entry")

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# render each encyclopedia page
def title(request, entry):

    # if entry does not exist, error page
    if util.get_entry(entry) is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"the page for {entry} was not found"
        })

    # if entry does exist, fetch markdown for that page, convert to html
    return render(request, "encyclopedia/entry.html", {
        "title": entry,
        "body": markdown.markdown(util.get_entry(entry))
    })

# search for an encyclopedia entry
def search(request):
    query = request.POST['q'] # query from search form
    entries = util.list_entries() # list of all entries
    matches = [] # empty list to store partial matches

    for entry in entries:
        # if exact match, redirect to entry page
        if query.lower() == entry.lower():
            return HttpResponseRedirect(reverse("title", kwargs={
                "entry": entry
                }))
        # if partial match, add entry to partial match list
        if query.lower() in entry.lower():
            matches.append(entry)
    
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "matches": matches
    })

# create a new encyclopedia page
def new(request):
    # display empty entry form
    if request.method == "GET":
        return render(request, "encyclopedia/new.html", {
            "form": NewEntryForm()
        })
    # else if request method POST
    else:
        form = NewEntryForm(request.POST)
        if form.is_valid():
            # save title and entry
            title = form.cleaned_data["title"]
            body = form.cleaned_data["newentry"]
            alltitles = util.list_entries()

            # return error if the title entered already exists
            for t in alltitles:
                if title.lower() == t.lower():
                    return render(request, "encyclopedia/error.html", {
                        "message": f"the title {t} already exists"
                    })
            # save valid entry and redirect to the new page
            util.save_entry(title, body)
            return HttpResponseRedirect(reverse("title", kwargs={
                "entry": title
                }))
        else:
            # return invalid form back to user
            return render(request, "encyclopedia/new.html", {
                "form": form
            })

# edit any encyclopedia entry
def edit(request, title):
    if request.method =="GET":
        body = util.get_entry(title)
        preform = NewEntryForm(initial={'title': title, 'newentry': body})
        return render(request, "encyclopedia/edit.html", {
            "preform": preform
        })
    # if POST, save entry
    else:
        form = NewEntryForm(request.POST)
        if form.is_valid():
            # save cleaned title and entry
            title = form.cleaned_data["title"]
            body = form.cleaned_data["newentry"]

            # save entry and redirect to the updated page
            util.save_entry(title, body)
            return HttpResponseRedirect(reverse("title", kwargs={
                "entry": title
                }))
        else:
            # return invalid form back to user
            return render(request, "encyclopedia/new.html", {
                "form": form
            })

# display any random entry
def arbitrary(request):
    entrylist = util.list_entries() # all entry titles
    num = random.randrange(len(entrylist)) # pick a random number 1-total
    pick = entrylist[num] # get random title
    return HttpResponseRedirect(reverse("title", kwargs={
                "entry": pick
            }))
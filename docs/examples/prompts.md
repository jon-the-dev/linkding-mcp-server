# Example Prompts

This page provides example prompts you can use with Claude (Desktop or Code) when the LinkDing MCP Server is configured. These natural language prompts demonstrate how to interact with your bookmarks conversationally.

## Searching Bookmarks

### Basic Search

> "Search my bookmarks for Python"

> "Find bookmarks about machine learning"

> "Look for any bookmarks mentioning React"

### Search by Tag

> "Show me all bookmarks tagged with 'tutorial'"

> "What bookmarks do I have tagged as 'reference'?"

> "Find my 'to-read' bookmarks"

### Search Unread Items

> "What bookmarks haven't I read yet?"

> "Show me my unread articles"

> "Find unread bookmarks about JavaScript"

### Search Archived Items

> "Search my archived bookmarks for old tutorials"

> "What's in my bookmark archive about Python?"

> "Find archived items tagged 'deprecated'"

### Combined Searches

> "Find unread Python tutorials"

> "Show me React bookmarks I haven't read yet"

> "Search for machine learning articles in my unread list"

## Adding Bookmarks

### Simple Bookmark

> "Bookmark https://docs.python.org"

> "Save https://react.dev to my bookmarks"

> "Add this URL to my bookmarks: https://example.com/article"

### Bookmark with Tags

> "Bookmark https://fastapi.tiangolo.com with tags python, api, and framework"

> "Save https://tailwindcss.com tagged as css, framework, and frontend"

> "Add https://postgresql.org to my bookmarks with the database tag"

### Bookmark with Notes

> "Bookmark https://example.com/tutorial and note that it's a great beginner resource"

> "Save https://docs.example.com with a note: official documentation for the project"

> "Add this URL with the note 'recommended by colleague': https://example.com"

### Bookmark with Title

> "Bookmark https://example.com with the title 'My Favorite Resource'"

> "Save this URL as 'Python Best Practices': https://example.com/python-guide"

### Complete Bookmark

> "Bookmark https://example.com/advanced-guide with title 'Advanced Python', tags python and advanced, and note 'covers metaclasses and decorators'"

### Bookmark for Later

> "Save https://example.com/long-article as unread for later"

> "Bookmark this and mark it as unread: https://example.com/tutorial"

## Checking URLs

### Check Before Bookmarking

> "Is https://github.com already in my bookmarks?"

> "Check if I've saved https://python.org"

> "Have I bookmarked this URL before: https://example.com"

### Smart Bookmarking

> "Check if https://example.com is bookmarked, and if not, add it with tag 'new'"

> "Only bookmark https://docs.example.com if I don't already have it"

## Managing Tags

### List Tags

> "What tags do I have?"

> "Show me all my bookmark tags"

> "List my tag collection"

### Browse by Tag

> "Show all bookmarks with the 'python' tag"

> "What have I saved under 'tutorials'?"

> "List everything tagged 'work'"

### Discover Content

> "What categories of bookmarks do I have?"

> "Show me my most used tags"

> "What topics have I been saving bookmarks about?"

## Updating Bookmarks

### Update Tags

> "Add the 'important' tag to my Python documentation bookmark"

> "Change the tags on bookmark 123 to 'archived' and 'reference'"

> "Remove all tags from the old tutorial bookmark and add 'deprecated'"

### Update Notes

> "Add a note to my React bookmark: 'updated for version 18'"

> "Update the notes on bookmark 456 to say 'no longer maintained'"

### Mark as Read/Unread

> "Mark my FastAPI bookmark as read"

> "I've finished reading the machine learning article, mark it as read"

> "Mark bookmark 789 as unread so I remember to revisit it"

## Archiving Bookmarks

### Archive Items

> "Archive my old JavaScript framework bookmarks"

> "Move the jQuery tutorial to my archive"

> "Archive bookmark 123"

### Unarchive Items

> "Bring back the archived Python tutorial"

> "Unarchive bookmark 456"

> "Restore the React hooks bookmark from my archive"

### Archive Workflow

> "Find all bookmarks tagged 'outdated' and archive them"

> "Archive everything I've read about Vue 2"

## Organizing Workflows

### Daily Review

> "Show me what I bookmarked today"

> "What unread bookmarks do I have from this week?"

> "List my recent bookmarks"

### Research Sessions

> "I'm researching GraphQL. Show me what I already have bookmarked about it."

> "Find all my bookmarks related to databases"

> "What resources do I have about Docker?"

### Cleanup

> "Find bookmarks without any tags"

> "Show me old bookmarks I might want to archive"

> "What bookmarks have I not looked at in a while?"

### Project Organization

> "Show all bookmarks for my 'project-alpha' work"

> "Find resources I've saved for the website redesign"

> "List everything tagged with 'client-work'"

## Deleting Bookmarks

!!! warning "Permanent Action"
    Deletion is permanent. Consider archiving instead if you might need the bookmark later.

### Delete by ID

> "Delete bookmark 123"

> "Remove bookmark number 456 from my collection"

### Delete with Confirmation

> "Show me bookmark 123 so I can decide if I want to delete it"

> "What's in bookmark 789? I'm thinking of deleting it."

## Conversational Workflows

### Research Assistant

**You:** "I'm starting research on Kubernetes. What do I already have?"

**Claude:** *searches bookmarks for kubernetes-related content*

**You:** "Great, now add this new article I found: https://example.com/k8s-guide"

**Claude:** *checks for duplicates, then adds with appropriate tags*

**You:** "Tag all my Kubernetes bookmarks with 'devops' too"

### Reading List Management

**You:** "What's on my reading list?"

**Claude:** *shows unread bookmarks*

**You:** "I just finished the React tutorial, mark it as read"

**Claude:** *updates bookmark status*

**You:** "And archive the old Angular one, I don't need it anymore"

### Content Curation

**You:** "Show me all my Python bookmarks"

**Claude:** *lists Python-tagged bookmarks*

**You:** "Which ones are tutorials?"

**Claude:** *filters for tutorial tag*

**You:** "Add all of those to a new 'python-learning' tag"

## Tips for Effective Prompts

### Be Specific

Instead of: "Find stuff"

Try: "Find bookmarks about React hooks tutorials"

### Use Natural Language

The server understands context, so you can say:

- "Bookmark this" (when you've mentioned a URL)
- "Add that to my collection" (referring to a previous URL)
- "Tag it with python" (referring to a bookmark you're discussing)

### Chain Actions

You can ask Claude to perform multiple related actions:

> "Check if https://example.com is bookmarked, and if not, add it with tags 'new' and 'to-read'"

### Ask for Help

> "What can you do with my bookmarks?"

> "How do I organize my bookmarks better?"

> "What's the best way to find old tutorials I've saved?"

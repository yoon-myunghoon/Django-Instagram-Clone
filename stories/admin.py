from django.contrib import admin

from stories.models import Story, StoryStream

admin.site.register(Story)
admin.site.register(StoryStream)



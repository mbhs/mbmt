from functools import partial

from django.shortcuts import render


index = partial(render, template_name="index.html")
info = partial(render, template_name="info.html")
about = partial(render, template_name="about.html")
archive = partial(render, template_name="archive.html")
rules = partial(render, template_name="rules.html")
topics = partial(render, template_name="topics.html")
registration = partial(render, template_name="registration.html")

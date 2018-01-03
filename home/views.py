from functools import partial

from django.shortcuts import render


index = partial(render, template_name="home/index.html")
info = partial(render, template_name="home/info.html")
about = partial(render, template_name="home/about.html")
archive = partial(render, template_name="home/archive.html")
rules = partial(render, template_name="home/rules.html")
topics = partial(render, template_name="home/topics.html")
registration = partial(render, template_name="home/registration.html")

import re

from django import template
from django_nav.base import nav_groups

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_nav(context, nav_group, *args, **kwargs):

    def check_conditional(of):
        conditional = of.conditional.get('function')
        return conditional and not conditional(context,
                                           *of.conditional['args'],
                                           **of.conditional['kwargs'])

    def build_options(nav_options, path, *args, **kwargs):
        out = []
        for option in nav_options:
            option = option()

            if check_conditional(option): continue

            option.is_child = True
            option.active = False
            option.active = option.active_if(option.get_absolute_url(), path)
            option.option_list = build_options(option.options, path, *args, **kwargs)
            out.append(option)

        return out

    out = []
    for nav in nav_groups[nav_group]:
        if check_conditional(nav): continue

        path = context['request'].path
        if hasattr(nav, 'template_name'):
            nav.option_list = build_options(nav.options, path, template_name=nav.template_name)
        else:
            nav.option_list = build_options(nav.options, path)

        nav.active = False
        nav.is_root = True
        url = nav.get_absolute_url()
        nav.active = nav.active_if(url, path)

        out.append(nav)
    return out

@register.assignment_tag(takes_context=True)
def render_nav(context, nav_group, *args, **kwargs):
    tpl = kwargs.get('using', 'django_nav/nav.html')
    return template.loader.render_to_string(tpl, {
        'nav_group': nav_group,
        'classname': kwargs.get('classname', 'nav'),
        'nav_list': get_nav(context, nav_group, *args, **kwargs)})

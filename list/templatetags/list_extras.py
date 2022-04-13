from django import template
from django.utils.translation import gettext as _
register = template.Library()

@register.simple_tag
def range_inclusive(start, end):
    return map(str,range(int(start), int(end)+1))

@register.simple_tag
def month_name(index):
    index = str(index)
    if index == "1":
        return _("January")
    elif index == "2":
        return _("February")
    elif index == "3":
        return _("March")
    elif index == "4":
        return _("April")
    elif index == "5":
        return _("May")
    elif index == "6":
        return _("June")
    elif index == "7":
        return _("July")
    elif index == "8":
        return _("August")
    elif index == "9":
        return _("September")
    elif index == "10":
        return _("October")
    elif index == "11":
        return _("November")
    elif index == "12":
        return _("December")

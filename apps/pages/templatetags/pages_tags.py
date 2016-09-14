from django import template
import importlib


register = template.Library()


@register.tag(name="evaluate")
def do_evaluate(parser, token):
    """
    tag usage {% evaluate object.textfield %}
    """
    try:
        tag_name, variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return EvaluateNode(variable)


class EvaluateNode(template.Node):
    def __init__(self, variable):
        self.variable = template.Variable(variable)

    def render(self, context):
        try:
            content = self.variable.resolve(context)
            t = template.Template(content)
            return t.render(context)
        except template.VariableDoesNotExist, template.TemplateSyntaxError:
            return 'Error rendering', self.variable


@register.inclusion_tag('pages/form.html', name='render_form', takes_context=True)
def render_form(context, module, klass):
    Klass = getattr(importlib.import_module(module), klass)
    if context['request'].method == 'POST':
        form = Klass(context['request'].POST)
        if form.is_valid():
            pass
    else:
        form = Klass()
    return {'form': form}

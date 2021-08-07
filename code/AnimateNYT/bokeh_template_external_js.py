"""
Created: July 2020
Author: TheDrDOS

Generate a template for Bokeh to use in it's html generation to supply external
Javascript resources, e.g. jquary.

Use the function template() to generate the template.
Example:
    import bokeh_template_external_js as tej
    external_src_template = tej.template('jquary')
    produces a template with jquary support
    Used as follows:
    from bokeh.io import output_file, save
    ....
    save(layout,template=external_src_template)
"""
externals = {
'jquary':
"""
    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
""",
'gzip':
"""
   <script src="https://rawgit.com/nodeca/pako/master/dist/pako_inflate.min.js"></script>
""",
'pako':
"""
   <script src="https://rawgit.com/nodeca/pako/master/dist/pako_inflate.min.js"></script>
""",
}

# The following is the standard template that bokeh.io save and show use
# Sourced from: https://docs.bokeh.org/en/latest/docs/reference/core/templates.html
# Specifically from the section on FILE = <Template 'file.html'> ... Template:file.html
external_src_template = {
    'pre':
"""
{% from macros import embed %}

<!DOCTYPE html>
<html lang="en">
  {% block head %}
  <head>
    {% block inner_head %}
      <meta charset="utf-8">
      <title>{% block title %}{{ title | e if title else "Bokeh Plot" }}{% endblock %}</title>
      {% block preamble %}{% endblock %}
      {% block resources %}
        {% block css_resources %}
          {{ bokeh_css | indent(8) if bokeh_css }}
        {% endblock %}
        {% block js_resources %}
          {{ bokeh_js | indent(8) if bokeh_js }}
        {% endblock %}
      {% endblock %}
      {% block postamble %}
          <!-- ############################################### -->
          <!-- Custom Added Code To Provide External Resources -->
""",
'post':
"""
          <!-- ############################################### -->
      {% endblock %}
    {% endblock %}
  </head>
  {% endblock %}
  {% block body %}
  <body>
    {% block inner_body %}
      {% block contents %}
        {% for doc in docs %}
          {{ embed(doc) if doc.elementid }}
          {% for root in doc.roots %}
            {% block root scoped %}
              {{ embed(root) | indent(10) }}
            {% endblock %}
          {% endfor %}
        {% endfor %}
      {% endblock %}
      {{ plot_script | indent(8) }}
    {% endblock %}
  </body>
  {% endblock %}
</html>
""",
}

def template(ext=''):
    """
    Make the template with the external resources
    Example: template('jquary')
    Input: list of strings, supported extensions are
        'jquary'
        anything else will be added literally, use the format:

    """
    if not isinstance(ext, list): ext = [ext]
    ext_template = external_src_template['pre']

    for e in ext:
        if e in externals:
            ext_template = ext_template+externals[e]
        else:
            ext_template = ext_template+e
    ext_template = ext_template+external_src_template['post']
    return ext_template

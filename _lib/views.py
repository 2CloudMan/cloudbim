from djangomako.shortcuts import render_to_string


def commonheader(title, section, user, padding="90px"):
  """
  Returns the rendered common header
  """
  return render_to_string("common_header.mako", {

  })


def commonfooter(messages=None):
  """
  Returns the rendered common footer
  """

  return render_to_string("common_footer.mako", {

})
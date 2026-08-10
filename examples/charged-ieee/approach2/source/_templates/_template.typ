// Custom template for charged-ieee (Approach 2)
// This template wraps the charged-ieee template and transforms
// Sphinx's simple author strings into IEEE's required format

#import "@preview/charged-ieee:0.1.4": ieee

#let project(
  title: "",
  authors: (),
  date: none,
  toctree_maxdepth: 2,
  toctree_numbered: false,
  toctree_caption: "Contents",
  papersize: "a4",
  fontsize: 11pt,
  // CONF-12/D-I: the extension now auto-derives `lang` from Sphinx's
  // `language` config on every non-package template route, including this
  // explicit `typst_template`. Declared (not forwarded into `ieee.with()`,
  // which has no such parameter) per the published nine-parameter
  // contract (D-A, templates.rst) -- omitting it would abort the compile
  // with `unexpected argument: lang`.
  lang: "en",
  body
) = {

  // Transform simple author strings into IEEE author format
  // This demonstrates the flexibility of custom templates
  let ieee_authors = authors.map(name => (
    name: name,
    department: "Computer Science",
    organization: "Massachusetts Institute of Technology",
    location: "Cambridge, MA",
    email: lower(name.split(" ").at(0)) + ".doe@mit.edu"
  ))

  // Define paper-specific parameters
  let ieee_abstract = [
    This paper presents novel approaches to machine learning
    applications in computer vision. We demonstrate state-of-the-art
    results on benchmark datasets and provide comprehensive analysis
    of our methodology.
  ]

  let ieee_keywords = (
    "Machine Learning",
    "Computer Vision",
    "Deep Learning",
    "Neural Networks"
  )

  // Apply IEEE template with transformed parameters.
  // No `bibliography:` argument: this sample carries no bibliography file,
  // and no build step places one beside the emitted document.
  show: ieee.with(
    title: title,
    authors: ieee_authors,
    abstract: ieee_abstract,
    index-terms: ieee_keywords,
    paper-size: papersize,
  )

  // Document body
  body
}

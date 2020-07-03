from .utils import render

from supermoms import app

@app.errorhandler(404)
def serve_404(e):
  return render("error_template.html", head = "Page Not Found", message = "The page you were looking for was not found."), 404

@app.errorhandler(403)
def serve_403(e):
  return render("error_template.html", head = "Permission Denied", message = "You do not have permission to access this page."), 403

@app.errorhandler(500)
def serve_500(e):
  return render("error_template.html", head = "Internal Error", message = "An internal error has occurred. Please try again later."), 500
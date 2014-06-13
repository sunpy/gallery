{%- extends 'full.tpl' -%}

{% block header %}
<meta name="viewport" content="width=device-width, initial-scale=1" />

<title></title>

{{ super() }}

<link href='http://fonts.googleapis.com/css?family=Open+Sans:200,300,400italic,400,700' rel='stylesheet' type='text/css' />
<!-- Bootstrap core CSS -->
<link href="http://sunpy.github.io/css/bootstrap.min.css" rel="stylesheet">

<link href="http://sunpy.github.io/docs-assets/css/sunpy.css" rel="stylesheet">

{%- endblock header %}

{% block body %}
<body>
<header class="navbar navbar-inverse navbar-fixed-top bs-docs-nav" role="banner">
  <div class="container">
    <div class="navbar-header">
      <button class="navbar-toggle" type="button" data-toggle="collapse" data-target=".bs-navbar-collapse">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a href="http://sunpy.github.io/gallery/index.html" class="navbar-brand">SunPy Gallery</a>
    </div>
  </div>
</header>
<div class="container bs-docs-container" style="margin-top: 50px;">
{{ super() }}
</div>
<!-- ================================================== -->
<!-- Placed at the end of the document so the pages load faster -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
<script src="http://sunpy.github.io/js/bootstrap.js"></script>

<script src="http://sunpy.github.io/docs-assets/js/holder.js"></script>

<script src="http://sunpy.github.io/docs-assets/js/application.js"></script>
<!-- This javascript hides tracebacks, but inserts a button to
     let the user toggle showing the full traceback. -->
<script type='text/javascript'>
    var parent = $('.output_pyerr');
    var b = $("<button></button><br>").appendTo(parent);
    b.attr('name', 'toggle_err');
    b.html('Show/hide full traceback');
    b.attr("class", "btn");

    $('button[name=toggle_err]').click(function() {
        $(this).parent().children('pre').toggle();
        $(this).parent().parent().children('.prompt').toggle();
        $(this).parent().parent().children('.prompt').toggle();
    });

    $('.output_pyerr pre').hide();

</script>

{%- endblock body %}

{% extends "gis/google/google-map.js" %}
{% block controls %}
{{ js_module }}.{{ dom_id }}.addControl(new GSmallMapControl());
{{ js_module }}.{{ dom_id }}.addControl(new GMapTypeControl());
{{ js_module }}.{{ dom_id }}.setMapType({{ maptype }});
{% endblock %}
{% block load_extra %}

{% for ts in timeseries %}{{ js_module }}.{{ dom_id }}_poly{{ forloop.counter }}.colors = {{ ts }};
{% endfor %}

{{ js_module }}.time_steps = {{ timesteps }};

{{ js_module }}.set_step = function(s) {
	//TODO find a way to loop only on polygons	
	for (poly in {{ js_module }}) {
		if (poly.indexOf("poly") >= 0) {
			{{ js_module }}[poly].setFillStyle({color:{{ js_module }}[poly].colors[s]});
		}
	}	
}
	
{% endblock %}

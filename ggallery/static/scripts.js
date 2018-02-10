
var clear_modal = function() {
  var mod = document.getElementsByClassName("modal-body")[0];
  var mod_title = document.getElementsByClassName("modal-title")[0];
  mod_title.innerHTML = '';
  while (mod.hasChildNodes()) {
    mod.removeChild(mod.firstChild);
  }
};


var display_image = function (image, title) {
  clear_modal();
  var mod = document.getElementsByClassName("modal-body")[0];
  var mod_title = document.getElementsByClassName("modal-title")[0];
  var mod_img = document.createElement('img');
  mod_img.classList.add("img-responsive");
  mod_img.classList.add("center-block");

  if (title != 'None')
    mod_title.innerHTML = title;

  $.post('/get_image', {'image_id':image}, function(d) {
    d = JSON.parse(d);
    console.log(d);

    mod_img.setAttribute('src', d['scale']);
    mod.appendChild(mod_img);

    if (d['code']) {
      var p = document.createElement('pre');
      var c = document.createElement('code');
      p.style = "margin-top: 10px";
      c.innerHTML = d['code'];
      p.appendChild(c);
      mod.appendChild(p);
    }

    $("#main_modal").modal();
  });
};

var populateRMSelect = function() {
  var gallery = document.getElementById('rm_gallery').value;
  var selector = document.getElementById('rm_img_id');

  while (selector.hasChildNodes()) {
    selector.removeChild(selector.firstChild);
  }

  $.post('/get_img_list', {'gallery':gallery}, function(d) {
    d = JSON.parse(d);

    for (var i=0; i<d.length; i++) {
      var op = document.createElement('option');
      op.innerHTML = d[i]['image'];
      selector.appendChild( op );
    }
  });
};

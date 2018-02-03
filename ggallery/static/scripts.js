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
      c.innerHTML = d['code'];
      p.appendChild(c);
      mod.appendChild(p);
    }

    $("#main_modal").modal();
  });
};

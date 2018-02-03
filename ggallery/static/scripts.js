var clear_modal = function() {
  var mod = document.getElementsByClassName("modal-body")[0];
  while (mod.hasChildNodes()) {
    mod.removeChild(mod.firstChild);
  }
};

var display_image = function (image) {
  clear_modal();
  var mod = document.getElementsByClassName("modal-body")[0];
  var mod_img = document.createElement('img');
  mod_img.setAttribute('src', image);
  mod.appendChild(mod_img);
  $("#main_modal").modal();
};

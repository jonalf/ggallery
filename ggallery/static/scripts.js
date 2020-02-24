var clear_modal = function() {
  var mod = document.getElementsByClassName("modal-body")[0];
  var mod_title = document.getElementsByClassName("modal-title")[0];
  mod_title.innerHTML = '';
  while (mod.hasChildNodes()) {
    mod.removeChild(mod.firstChild);
  }
};

var display_image = function (image, title, year) {
  clear_modal();
  var mod = document.getElementsByClassName("modal-body")[0];
  var mod_title = document.getElementsByClassName("modal-title")[0];
  var mod_img = document.createElement('img');
  mod_img.classList.add("img-responsive");
  mod_img.classList.add("center-block");

  if (title != 'None')
    mod_title.innerHTML = title;

    $.post('/get_image', {'image_id':image, 'year':year}, function(d) {
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



var upload_processing = function() {
  var mod_title = document.getElementsByClassName("modal-title")[0];

  mod_title.innerHTML = 'Please wait while the server uploads and processes your image';

  $("#main_modal").modal();
};

var upload = function(e) {
    console.log('upload!');
    upload_processing();
    var imgFile = document.getElementById('img_file');

    //if no file selected, do nothing
    if (imgFile.files.length == 0) {
	alert('No File Selected');
	window.location = 'http://gallery.stuycs.org/upload';
	return;
    }
    var data = new FormData();
    data.append('gallery', document.getElementById('gallery').value);
    data.append('img_file', imgFile.files[0]);
    data.append('img_code', document.getElementById('img_code').value);
    data.append('title', document.getElementById('title').value);
    console.log(data);
    //create ajax call
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
	if(request.readyState == 4) {
	    try {
		var resp = JSON.parse(request.response);
	    }
	    catch (e) {
		var resp = {
		    status: 'error',
		    data: 'error'//'Unknown error occurred: [' + request.responseText + ']'
		};
	    }
	    console.log( resp.status );
	    if (resp.status == 'nofile') {
		window.alert('No File Selected');
		window.location = 'http://gallery.stuycs.org/upload';
	    }
	    if (resp.status == 'format') {
		//console.log(resp.status);
		window.location = 'http://gallery.stuycs.org/upload';
		//window.alert('Your image must be a .png, .gif or .jpg file');
	    }

	    if (resp.status == 'nogo') {
		window.location = 'http://gallery.stuycs.org/upload';
	    }
	    if (resp.status == 'go') {
		window.location = 'http://gallery.stuycs.org';
	    }
	    
	}
    };

    request.upload.addEventListener('progress',function(e) {
	//_progress.style.width = Math.ceil(e.loaded/e.total) * 100 + '%';
	console.log(e.loaded + ' ' + e.total);
    }, false);

    request.open('POST', '/send_file');
    request.send(data);
}

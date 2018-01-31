var CURRENT_TERM = '2';
var CURRENT_YEAR = '2016';

var PREFIXES = {
    'english' : 'E',
    'history' : 'H',
    'math' : 'M',
    'language' : 'F',
    'gym' : 'PE',
    'science' : 'S',
    'lab' : 'SLAB',
    'performer' : 'UU'
};


var toggle_hr_list = function(hr) {
    //console.log(hr);
    var container = document.getElementById(hr+'list');
    if (container)
	container.remove();
    else
	populate_hr_list(hr);
};

var clear_hr_list = function(hr) {
    
    var container = document.getElementById(hr+'list');
    container.remove();
};

var populate_hr_list = function( hr ) {
    //console.log('populate ' + hr );
    $.post( '/hrlookup', {'hr' : hr}, function(d) {
	d = JSON.parse(d);

	var container = document.getElementById(hr);
	var students = document.createElement('div');
	students.id = hr+'list';
	students.classList.add('list-group');

	for (var i=0; i<d.length; i++)  {
	    var link = document.createElement('a');
	    link.classList.add('list-group-item');
	    var l = '/lookup?osis=' + d[i][0];
	    link.setAttribute('href', l);
	    link.innerText = d[i][1] + ' ' + d[i][2] + ' ' + d[i][0];
	    students.appendChild(link);
	}	
	container.appendChild(students);
    });
};


var populate_table = function( osis ) {
    
    $.post( '/lookup2', {'osis' : osis}, function(d) {
	d = JSON.parse(d);
	//console.log(d);
	
	var subjects = Object.keys( d );

	for (var s=0; s < subjects.length; s++) {
	    var subject = subjects[s];
	    var courses = d[ subject ];
	    
	    //console.log(subject);
	    if ( subject == 'math' ||
		 subject == 'language' ||
		 subject == 'performer'
		 //subject == 'tech'
	       )
		update_list( courses, subject );
	    else if ( subject == 'english' ||
		      subject == 'history' ||
		      subject == 'gym' ||
		      subject == 'science' ||
		      subject == 'lab' ||
		      subject == 'art' ||
		      subject == 'music' ||
		      subject == 'cs' ||
		      subject == 'drafting' ||
		      subject == 'health' ||
		      subject == 'tech'
		    )
		update_reqs( courses, subject );
	    else if ( subject == 'other' )
		update_other( courses );
	}	
    });    
};

//THIS NEEDS TO CHANGE TO REFLECT IF THE CLASS WAS TAKEN WHILE A SENIOR
var is_senior_elective = function( year ) {
    var hrdiv = document.getElementById('hrid');
    var hrtext = hrdiv.innerHTML.split(' ')[1];
    return hrtext[0] == '7' && year == CURRENT_YEAR;
};

var update_fail_or_other = function( course, year, boxID ) {

    console.log('year: ' + year + ' boxID: ' + boxID);
    
    if ( is_senior_elective(year) && boxID == 'other') {
	//do senior elective thing
	var se1 = document.getElementById( 'SEL1' );
	var se2 = document.getElementById( 'SEL2' );
	if ( !se1.classList.contains("done") )
	    boxID = 'SEL1';
	else if ( !se2.classList.contains("done") )
	    boxID = 'SEL2';
    }
    var otherBox = document.getElementById( boxID );    
    var text = '';
    console.log(course);
    text+= course['course'] + ' ';

    if ( boxID == 'other' || boxID == 'fail') {
	text+= course['course title'] + ' ';
	text+= course['mark'] + '<br>';
    }
    else
	otherBox.classList.add('done');
    otherBox.innerHTML+= text;
};

var update_other = function( courses ) {
    for (var i=0; i<courses.length; i++) {
	//console.log(courses[i]);
	
	if (passed( courses[i] ))
	    update_fail_or_other(courses[i], courses[i]['year'], 'other');	
	else
	    update_fail_or_other(courses[i], false, 'fail');
    }
};

var update_reqs = function( courses, subject ) {
    //console.log('begin update reqs');
    for (var i=0; i < courses.length; i++) {
	//console.log(courses[i]);
	var reqs = courses[i]['requirements'];
	if ( reqs.length != 0 ) {
	    for (var j=0; j < reqs.length; j++ ) {
		var req = reqs[j][1];
		//console.log('req: ' + req);
		var box = document.getElementById( req );
		
		if ( passed(courses[i]) ) {
		    if ( box ) {
			box.classList.remove("failed");
			box.classList.add("done");
			box.innerHTML = box.innerHTML + '<br>' + reqs[j][0];
		    }
		    else {
			update_fail_or_other(courses[i], courses[i]['year'], 'other');
		    }
		}
		else {		    
		    if ( box && !(box.classList.contains("done"))) {
			box.classList.add("failed");
			box.innerHTML = box.innerHTML + '<br>' + reqs[j][0];
		    }
		    update_fail_or_other(courses[i], false, 'fail');
		}		
	    }
	}
    }
    //console.log('end update reqs');
};

var update_list = function( courses, subject ) {
    console.log('begin update list');
    var failures = 0;
    for (var i=0; i < courses.length; i++) {
	var code = courses[i]['course'];
	var prefix = PREFIXES[ subject ];
	var id2 = i + 1 - failures;
	var id = prefix + id2;
	var box = document.getElementById( id );

	console.log(courses[i]);
	
	if ( passed(courses[i]) ) {
	    console.log('passed');
	    if ( box  == null ) {
		update_fail_or_other(courses[i], courses[i]['year'], 'other');
	    }
	    
	    else {
		var j = 1;
		while ( box.classList.contains("done") ) {
		    id2 = (i + 1 - failures + j);
		    if ( id2 > 8 ) {			
			update_fail_or_other( courses[i], courses[i]['year'], 'other');
			break;
		    }
		    id = prefix + id2;
		    j++;
		    box = document.getElementById( id );
		}
		if ( id2 <= 8 ) {
		    box.classList.remove("failed");
		    box.classList.add( "done" );
		    box.innerHTML+= '<br>' + code;
		}
	    }
	}//end if passed
	else {
	    if ( box  == null ) {
		update_fail_or_other(courses[i], false, 'fail');
		failures++;
	    }
	    else {
		j = 1;
		while ( box.classList.contains("failed") ||
			box.classList.contains("done") ) {
		    id2 = (i + 1 - failures + j);
		    id = prefix + id2;
		    if ( id2 > 8 )
			break;
		    j++;
		    box = document.getElementById( id );
		}
		failures++;
		if ( id2 <= 8 ) {
		    box.classList.add( "failed" ); 	
		    box.innerHTML+= '<br>' + code;
		}
		update_fail_or_other(courses[i], false, 'fail');
	    }
	}
    }
    //console.log('end update list');
};

var passed = function( course ) {
    var grade = course['mark'];

    if ( Number(grade) )
	return Number(grade) >= 65;
    else if (grade == 'P' ||
	     grade == 'S' ||
	     grade == 'E' ||
	     grade == 'CR' )
	return true;
    else
	return false;
};

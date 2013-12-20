// ------------------------------------------------------------------------------------------------------------------
// Facebook
// ------------------------------------------------------------------------------------------------------------------

window.fbAsyncInit = function() {
    FB.init({
        appId   : '234778956683382',
        oauth   : true,
        status  : true, // check login status
        cookie  : true, // enable cookies to allow the server to access the session
        xfbml   : true // parse XFBML
    });

    /**
     * FB.Event Suscribe
     * Detect when an user press like button 
     */

    FB.Event.subscribe('edge.create', function(href, widget) {
            
            // TODO: Revisar seguridad de esta llamada
            var meguzId = document.URL.split("/meguz/")[1].split("/")[0];                
            $.ajax({
                type: "POST",
                url: '/usuario/suscribe/'+meguzId+'/', 
                success: function(data) { 

                    console.log("data: "+data);
                    if(data.search('NOT_FOUND') > -1) {

                        console.log("Meguz "+meguzId+" no encontrado...");

                    } else if(data.search('FORBIDDEN') > -1) {
                        
                        console.log("Acceso restringido");

                    } else if(data.search("FINISH") > -1) {
                        // TODO: Implement instance where fix number of likes using
                        // https://graph.facebook.com/fql?q=SELECT like_count FROM link_stat WHERE url='PAGE URL'
                        console.log("FINISH")
                        $.post('/meguz/validate-finish/', {meguz_id: meguzId, url: document.URL}, function(response){
                            console.log(response);
                        })
                        
                    } else {

                        console.log("DONE");                        
                        
                    }
                }
            });
            

                    
        }

    );

  };

// ------------------------------------------------------------------------------------------------------------------
// Login / logout
// ------------------------------------------------------------------------------------------------------------------

function fbLogin(){
    FB.login(function(response) {

        if (response.authResponse) {
            //console.log(response); // dump complete info
            access_token = response.authResponse.accessToken; //get access token
            user_id = response.authResponse.userID; //get FB UID

            FB.api('/me', function(userinfo) {
         
                var request = $.ajax({
                    type: "POST",
                    url: '/usuario/login', 
                    data: userinfo,  
                    success: function(data) {
                        setCookie('fbmgz_234778956683382', data,1);
                        setCookie('user_name', userinfo.first_name,1);
                        setCookie('user_avatar', 'http://graph.facebook.com/' + userinfo.id + '/picture',1); 
                        userPanelLogout();  
                    },
        		    error: function(jqXHR, textStatus, errorThrown) {
                        alert (errorThrown);
                    }
                });
    
            });

        } else {
            //user hit cancel button
            console.log('User cancelled login or did not fully authorize.');

        }
    }, {
        scope: 'offline_access,user_birthday,user_likes,email'
    });
}

function fbLogout() {
    setCookie('fbmgz_234778956683382', '', -1);
    setCookie('user_name', '', -1);
    setCookie('user_avatar', '', -1);
    userPanelLogin();    
}

function isLogged() {
    var user_name = getCookie('user_name');
    if(typeof user_name == "undefined")  return false;
    return true;
}

function userPanel() {
    if(!isLogged()) userPanelLogin();
    else userPanelLogout();    
}

function userPanelLogin() {
    // Crear view userpanel/login y cargar nombre + link a cuenta usuario + btn logout
    $('#userLogOut').show();
    $('#userLogIn').hide();
    
    btnParticipar();
}

function userPanelLogout() {
    // Crear view userpanel/logout y cargar btn login + crsf_token
    var userLogIn = $('#userLogIn').html();
    userLogIn = userLogIn.replace('[[username]]', getCookie('user_name'));
    userLogIn = userLogIn.replace('[[useravatar]]', '<img src="'+getCookie('user_avatar')+'"">');  
    $('#userLogIn').html(userLogIn);
    $('#userLogIn').show();
    $('#userLogOut').hide();

    btnParticipar();
}

function toggleMenu() {
    var btn = $('.menu_usuario_nav');
    if(btn.css("display") == "none") btn.show();
    else btn.hide();
}

// ------------------------------------------------------------------------------------------------------------------
// Funciones generales 
// ------------------------------------------------------------------------------------------------------------------

function setCookie(c_name,value,exdays) {
    var exdate=new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var c_value=escape(value) + ((exdays==null) ? "" : "; expires="+exdate.toUTCString());
    document.cookie=c_name + "=" + c_value + "; path=/";
}

function getCookie(c_name) {
    var i,x,y,ARRcookies=document.cookie.split(";");
    for (i=0;i<ARRcookies.length;i++) {
        x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
        y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
        x=x.replace(/^\s+|\s+$/g,"");
        if (x==c_name) {
            return unescape(y);
        }
    }
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

// ------------------------------------------------------------------------------------------------------------------
// Premios
// ------------------------------------------------------------------------------------------------------------------

function participar(prize_id) {
    if(!isLogged()) fbLogin();
    else document.location = "/usuario/premios/" + prize_id + '/participar';
}

function participarForm(offer_id) {

    $('.error').hide('fast');
    var title = $('#id_title').val();
    var description = $('#id_description').val();
    var file = $("#id_file").val();
    var is_valid = true;

    if(title == '') {
        is_valid = false;
        $('#error_title').html('Debes ingresar un título');
    }

    if(description == '') {
        is_valid = false;
        $('#error_description').html('Debes ingresar una descripción');
    }

    if(!file) {
        is_valid = false;
        $('#error_file').html('Debes ingresar un video');
    }

    if(is_valid) {

        participarLoader();
        $.ajax({
            async: false,
            type: 'POST',
            url: '/premios/participar/form/' + offer_id + '/' + getCookie('fbmgz_234778956683382') + '/',
            data: $('#form_participar').serialize(),
            success: function(responseText) {
                if(jQuery.isNumeric(responseText)) {
                    console.log("responseText");
                    return true;
                }
            }
        });

    } else {

        $('.error').fadeIn();
        return false;

    }        

}

function participarLoader() {
    var height = Math.max($(document).height(), $(window).height())
    $('#loader_container').css('height', height);
    $('#loader_container').slideDown();
}



function editMeguz(meguz_id) {

    $('.error').hide('fast');
    var title = $('#id_title').val();
    var description = $('#id_description').val();
    var file = $("#id_file").val();
    var is_valid = true;

    if(title == '') {
        is_valid = false;
        $('#error_title').html('Debes ingresar un título');
    }

    if(description == '') {
        is_valid = false;
        $('#error_description').html('Debes ingresar una descripción');
    }

    if(is_valid) {

        $.ajax({
            async: false,
            type: 'POST',
            url: '/meguz/edit/form/' + meguz_id + '/' + getCookie('fbmgz_234778956683382') + '/',
            data: $('#form_participar').serialize(),
            success: function(responseText) {
                console.log(responseText);
            },
            complete: function(data) {

                if( $('#id_file').val() != "" ) {
                    participarLoader();
                    $.post('/meguz/'+meguz_id+'/eliminar-video/', $('#form_participar').serialize(), function(data){                    
                        $('#submit_meguz_form').click()
                    });      

                }
            }

        });

    }
}

function confirmDelete() {
    if(confirm("¿Seguro que deseas eliminar este meguz? Perderas todos los votos..."))
        return true;    
    return false;
}

function btnParticipar() {    
    if(isLogged()) {
        $('.btn-participar').html('<span class="bt_inicio_sesion_ok">Participar</span>');
        $('.btn-participar').removeClass('not-login');
    } else {
        $('.btn-participar').html('<span class="bt_inicio_sesion bt_inicio_sesion_txt">Inicia sesión para Participar</span>');
        $('.btn-participar').addClass('not-login');
    }
}

function closeWelcome() {
    $('.welcome').slideUp();
    // TODO: Set cookie to avoid showing welcome again
}
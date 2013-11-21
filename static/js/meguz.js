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

                var csrftoken = getCookie('csrftoken');
                
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                            // Send the token to same-origin, relative URLs only.
                            // Send the token only if the method warrants CSRF protection
                            // Using the CSRFToken value acquired earlier
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    }
                });
                
                var request = $.ajax({
                    type: "POST",
                    url: '/user/login', 
                    data: userinfo,  
                    success: function(data) {
                        setCookie('fbmgz_234778956683382', data, 7);
                        setCookie('user_name', userinfo.first_name, 7);
                        setCookie('user_avatar', 'http://graph.facebook.com/' + userinfo.id + '/picture', 7); 
                        userPanelLogout();  
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
    else document.location = "/premios/participar/" + prize_id;
}

function btnParticipar() {    
    if(isLogged()) {
        $('.btn-participar').html('Participar');
        $('.btn-participar').removeClass('not-login');
    } else {
        $('.btn-participar').html('<p class="small">Inicia sesión para</p>Participar');
        $('.btn-participar').addClass('not-login');
    }
}
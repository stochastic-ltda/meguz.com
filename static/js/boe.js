/*
 * Set action 
 * Change the multimedia form action depending of the selected media_type
 */
function set_action(media_type) {

	if(media_type == 'Y') {

		var post_url = $('#post_url').val()
		$('#multimedia_offer').attr('action', post_url)
		$('#input_image').hide()
		$('#input_video').show()
		$('#submit').val('Subir video')

	} else {

		$('#multimedia_offer').attr('action', '')	
		$('#input_image').show()
		$('#input_video').hide()
		$('#submit').val('Subir imagen')	

	}
}
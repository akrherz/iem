window.fbAsyncInit = function () {
  FB.Event.subscribe('comment.create', function(response){
    // Here you need to do a call to some service/script/application
    // to notify your administrator about new comment.
    // I'll use jQuery ajax to call server-side script to illustrate the flow 
    $.post('/fbcomments.php', {
      "action": "comment created",
      "url_of_page_comment_leaved_on": response.href,
      "id_of_comment_object": response.commentID
    });
  });
  
};

(function(d, s, id) {
	var js, fjs = d.getElementsByTagName(s)[0];
	if (d.getElementById(id)) return;
	js = d.createElement(s); js.id = id;
	js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=196492870363354";
	fjs.parentNode.insertBefore(js, fjs);
	}(document, 'script', 'facebook-jssdk'));
function makeFeed()
{
	var keywords = $("#keyword_input").val().replace(/[^0-9a-zA-Z]/g,",").split(",");
	var url = window.location.href + "find/all/" + keywords.join("_");
	$("#feed_link").attr("href", url);
	$("#feed_link").text(url);
	$("#google_link").attr("href", "http://fusion.google.com/add?source=atgs&feedurl="+encodeURI(url));
	addRSS(url,"feed_demo");
}

function addRSS(url, elementID)
{
	jQuery.getFeed({
	   url: url,
	   success: function(feed) {
	     var html = '';
            
            for(var i = 0; i < feed.items.length && i < 5; i++) {
            
                var item = feed.items[i];
                
                html += '<div class="feed_item"><h3>'
                + '<a href="'
                + item.link
                + '">'
                + item.title
                + '</a>'
                + '</h3>';
                
                html += '<div class="updated">'
                + item.updated
                + '</div>';
                
                html += '<div>'
                + item.description
                + '</div></div>';
            }
            
            jQuery('#'+elementID).html(html);
	   }
	});

}

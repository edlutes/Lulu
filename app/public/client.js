function loadTerms() {
  $.get('/terms', function(termResults) {
    var terms = Array();
    termResults.forEach(function(result) {
      terms.push("<li><a class='remove_term' href='#'>"+result.term+"</a></li>");
    });
    $("#terms").html(terms.join(""));
    loadTweets();
  });
}

function loadTweets() {
  $.get('/tweets', function(tweetResults) {
    var tweets = Array();
    tweetResults.forEach(function(result) {
      tweets.push("<li>"+result.tweet+"</li>");
    });
    $("#tweets").html(tweets.join(""));
    $("#tweet_count").html(tweetResults.length);
  });
}

$(function() {
  loadTweets();
  loadTerms();

  $('#terms').on("click", "a.remove_term", function(event) {
    event.preventDefault();
    $.ajax({
      url: "/terms/"+$(event.target).html(),
      type: "DELETE",
      success: function() {
        loadTerms();
      }
    });
  });

  $('form#new_term').submit(function(event) {
    event.preventDefault();
    $.ajax({
      url: "/terms",
      type: "POST",
      data: JSON.stringify({'term': $('#new_term input').val()}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function() {
        loadTerms();
      }
    });
  });

  $('form#new_tweet').submit(function(event) {
    event.preventDefault();
    $.ajax({
      url: "/tweets",
      type: "POST",
      data: JSON.stringify({'tweet': $('#new_tweet input').val(), 'username': 'webuser'}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function() {
        loadTweets();
      }
    });
  });
});

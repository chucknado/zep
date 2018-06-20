$(function() {

  $("#get-btn").click(function(event) {
    event.preventDefault();
    var search_str = $("#subject-field").val();
    getArticles(search_str);
  });

});

function getArticles(search_str) {
  var parameters = {
    action: "query",
    list: "search",
    srsearch: search_str,
    srlimit: 3,
    format: 'json'
  };

  $.ajax({
    url: 'https://en.wikipedia.org/w/api.php',
    data: parameters,
    type: 'POST',
    dataType: 'json',
    beforeSend: function(xhr){
      xhr.setRequestHeader('Api-User-Agent', 'MyChatApp/1.0 (chucknado@comcast.net)');
    }
  })
  .done(function(data) {
    console.log('success');
    console.log(data);
  })
  .fail(function(xhr) {
    console.log("status: " + xhr.status);
    console.log(xhr);
  });
}

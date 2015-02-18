$( document ).ready(function() {
    var urlsTable = $('#urls');
    var urlIdsTd = urlsTable.find('.url-id');

    //Раз во сколько миллисекунд опрашивать сервер на предмет появления полученных тайтлов
    var REQUESTS_INTERVAL = 5000;

    //id урлов как массив строк
    //Используется глобально для проверка ответов от урлов
    var ids;

    var interval;

    var requestTitlesButton = $('#request-titles');

    // В идеале запросы к торнадо нужно слать чанками, по 5 в одном, например
    $('#request-titles').click(function(e) {
        //Получение id всех урлов на странице
        ids = urlIdsTd.map(function() {return $(this).html();}).get();
        e.preventDefault();
        $('.title').html('');
        requestTitlesButton.addClass('disabled');
        requestTitles(ids.join())
    });

    //Запрос на инициализацию получения тайтла к Торнадо
    function requestTitles(urlIds) {
      $.ajax({
          url: 'initiate_requests/',
          dataType: 'json',
          data: 'urlIds=' + urlIds
        }).done(function(response) {
          // TODO проверка на успешный ответ
          interval = setInterval(function(){checkUrlResponses()}, REQUESTS_INTERVAL);
        });
    };

    function checkUrlResponses(){
        $.ajax({
              url: 'check_responses/',
              dataType: 'json',
              data: 'urlIds=' + ids.join()
              }).done(function(response) {
                  //Проходим по ответу от сервера, находим соответствующую строку, подставляем title, извлекаем id строки из параметров следующего запроса
                  for (key in response){
                      targetTr = urlIdsTd.filter(function() {
                            return $(this).text().trim() == key;
                        }).parents('tr');
                      targetTr.find('.title').html(response[key]);
                      //Если ключ не найден, то удалять id из списка не нужно
                      var idIndex = ids.indexOf(key)
                      if (idIndex !== -1) ids.splice(idIndex, 1);
                  }
              if (ids.length === 0){
                clearInterval(interval);
                requestTitlesButton.removeClass('disabled');
              }
        });
    }
});

var csrf_token,
    notification_url,
    websocket_url,
    redis_heartbeat;


$(document).ready(function(){
    initialRedis();
    getNotifications();

});

function initialRedis(){
    var ws4redis = WS4Redis({
       uri: websocket_url + 'notifications?subscribe-broadcast&publish-broadcast&echo',
       heartbeat_msg: redis_heartbeat,
       // receive a message though the Websocket from the server
       receive_message: function (msg) {
           getNotifications();
       }
   });
}

function getNotifications() {
    $.ajax({
        url: notification_url,
        data: {
            csrfmiddlewaretoken: csrf_token
        },
        type: "GET",
        success: function (response) {
            var unread_count = 0;
            var notifications = response.notifications;
            var dropdown = $("#notification-dropdown");
            dropdown.empty();

            /**
             * add li element for each notification
             * apply suitable class based on read or unread
             * click on each notification mark it as read
             */
            $.each(notifications, function() {
                var title_span = $("<span class='notif-title'></span>").text(this.title);
                var description_span = $("<span class='notif-description'></span>").text(this.description);
                var container = $('<a></a>').attr('onclick', 'readNotification('+this.id+')');
                var item = $("<li></li>");

                container.append(title_span);
                container.append(description_span);
                item.append(container);
                if(!this.read)item.addClass('notif-unread');
                dropdown.append(item);

                if(!this.read)unread_count++;
            });

            /** add read all button */
            var container = $('<a></a>').attr('onclick', 'readAllNotification()').text('Read All');
            var item = $("<li></li>");
            item.append(container);
            dropdown.append(item);

            if(unread_count != 0)
                $('#notif-badge').text(unread_count);
            else
                $('#notif-badge').hide();
        }
    });
}

function readNotification(id){
    $.ajax({
        url: notification_url,
        data: {
            id: id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            getNotifications();
        }
    });
}

function readAllNotification(){
    $.ajax({
        url: notification_url,
        data: {
            read_all: true,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            getNotifications();
        }
    });
}
document.getElementById('notiImg').addEventListener('click', function () {
    if(document.getElementById('notificationList') === null){
        const headerRight = document.getElementById('headerRight');
        let notiList = document.createElement('div');
        notiList.id = 'notificationList';
        headerRight.appendChild(notiList);
    }
    const container = document.getElementById('notificationList');

    setTimeout(() => {}, 500);

    if (container.style.display === 'none') {
        fetch('/notifications')
            .then(response => response.json())
            .then(data => {
                container.innerHTML = '';

                if (data.length === 0) {
                    container.innerHTML = '<p>No notifications</p>';
                } else {
                    data.forEach(notification => {
                        const div = document.createElement('div');
                        div.classList.add("notification");
                        div.style.backgroundColor = notification.read ? '#f9f9f9' : '#E6F0FE';

                        const title = document.createElement('strong');
                        title.classList.add("notiTitle");
                        title.textContent = notification.title;

                        const message = document.createElement('span');
                        message.classList.add("notiMessage");
                        message.textContent = notification.description;
                        message.style.display = 'block';

                        const time = document.createElement('small');
                        const date = new Date(notification.created_at);
                        time.textContent = date.toLocaleString();
                        time.style.color = '#888';

                        div.appendChild(title);
                        div.appendChild(message);
                        div.appendChild(time);

                        div.addEventListener('click', () => {
                            fetch(`/notifications/${notification.id}/read`, {method: 'POST'})
                                .then(res => {
                                    if (res.ok) {
                                        div.style.backgroundColor = '#f9f9f9';
                                        window.location.href = `/note/${notification.note_id}`
                                    }
                                });
                        });

                        container.appendChild(div);
                    });
                }

                container.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching notifications:', error);
                container.innerHTML = '<p>Error loading notifications</p>';
                container.style.display = 'block';
            });
    } else {
        container.style.display = 'none';
    }
});

// function updateNotificationBell() {
//     fetch('/notifications/unread_count')
//         .then(res => res.json())
//         .then(data => {
//             const notiImg = document.getElementById('notiImg');
//             if (data.count > 0) {
//                 notiImg.classList.add('red-bell');
//             } else {
//                 notiImg.classList.remove('red-bell');
//             }
//         })
//         .catch(err => {
//             console.error('Failed to fetch unread notification count:', err);
//         });
// }
//
// document.addEventListener('DOMContentLoaded', updateNotificationBell);

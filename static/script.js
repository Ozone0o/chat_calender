document.addEventListener('DOMContentLoaded', function () {
  const yearElement = document.getElementById('year');
  const monthElement = document.getElementById('month');
  const datesContainer = document.getElementById('datesContainer');
  const inputMessageElement = document.getElementById('inputMessage');
  const sendMessageBtn = document.getElementById('sendMessageBtn');
  const chatMessagesContainer = document.getElementById('chatMessages');

  const dateModal = document.getElementById('dateModal');
  const closeModalBtn = document.getElementById('closeModal');
  const modalDateTitle = document.getElementById('modalDateTitle');
  const modalDateContent = document.getElementById('modalDateContent');

  let now = new Date();
  let month = now.getMonth();
  let year = now.getFullYear();
  let daysInMonth = new Date(year, month + 1, 0).getDate();

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  let highlightedDates = [];

  function renderEventModal(clickedDate, eventsData) {
    modalDateTitle.textContent = `今日安排  ${clickedDate} ${months[month]} ${year}`;
    modalDateContent.innerHTML = '';

    eventsData.forEach((event, index) => {
      const eventDiv = document.createElement('div');
      eventDiv.className = 'event-block';
      eventDiv.innerHTML = `
        <strong>事件名称:</strong> ${event.event_name}<br>
        <strong>时间:</strong> ${event.time}<br>
        <strong>地点:</strong> ${event.location}<br>
        <strong>流程:</strong> ${event.process}<br>
      `;

      const deleteBtn = document.createElement('button');
      deleteBtn.textContent = '删除';
      deleteBtn.className = 'delete-btn';
      deleteBtn.addEventListener('click', () => {
        const dateObj = highlightedDates.find(date =>
          date.day === clickedDate && date.month === month && date.year === year
        );

        if (dateObj) {
          dateObj.events.splice(index, 1);

          const allDateItems = document.querySelectorAll('.date_item');
          allDateItems.forEach(item => {
            if (parseInt(item.textContent, 10) === clickedDate) {
              if (dateObj.events.length === 0) {
                // 删除该日期所有事件并移除高亮
                const idx = highlightedDates.indexOf(dateObj);
                highlightedDates.splice(idx, 1);
                item.classList.remove('event-day');
                delete item.dataset.event;
                dateModal.style.display = 'none';
              } else {
                item.dataset.event = JSON.stringify(dateObj.events);
                renderEventModal(clickedDate, dateObj.events);
              }
            }
          });
        }
      });

      eventDiv.appendChild(deleteBtn);
      modalDateContent.appendChild(eventDiv);
    });

    dateModal.style.display = 'block';
  }

  function renderCalendar() {
    yearElement.textContent = year;
    monthElement.textContent = months[month];
    datesContainer.innerHTML = '';

    const firstDay = new Date(year, month, 1).getDay();
    for (let i = 0; i < firstDay; i++) {
      datesContainer.innerHTML += '<div class="date_item"></div>';
    }

    for (let i = 1; i <= daysInMonth; i++) {
      let dateItem = document.createElement('div');
      dateItem.classList.add('date_item');
      dateItem.textContent = i;

      const dateEvents = highlightedDates.find(date => date.day === i && date.month === month && date.year === year);
      if (dateEvents) {
        dateItem.classList.add('event-day');
        dateItem.dataset.event = JSON.stringify(dateEvents.events);
      }

      dateItem.addEventListener('click', function () {
        const clickedDate = parseInt(dateItem.textContent, 10);
        const eventsData = dateItem.dataset.event ? JSON.parse(dateItem.dataset.event) : null;

        if (eventsData && eventsData.length > 0) {
          renderEventModal(clickedDate, eventsData);
        }
      });

      datesContainer.appendChild(dateItem);
    }
  }

  closeModalBtn.addEventListener('click', function () {
    dateModal.style.display = 'none';
  });

  window.addEventListener('click', function (event) {
    if (event.target === dateModal) {
      dateModal.style.display = 'none';
    }
  });

  document.getElementById('prevYearBtn').addEventListener('click', function () {
    year--;
    daysInMonth = new Date(year, month + 1, 0).getDate();
    renderCalendar();
  });

  document.getElementById('nextYearBtn').addEventListener('click', function () {
    year++;
    daysInMonth = new Date(year, month + 1, 0).getDate();
    renderCalendar();
  });

  document.getElementById('prevMonthBtn').addEventListener('click', function () {
    if (month > 0) {
      month--;
    } else {
      month = 11;
      year--;
    }
    daysInMonth = new Date(year, month + 1, 0).getDate();
    renderCalendar();
  });

  document.getElementById('nextMonthBtn').addEventListener('click', function () {
    if (month < 11) {
      month++;
    } else {
      month = 0;
      year++;
    }
    daysInMonth = new Date(year, month + 1, 0).getDate();
    renderCalendar();
  });

  sendMessageBtn.addEventListener('click', async function () {
    const message = inputMessageElement.value;
    if (message) {
      inputMessageElement.value = '';

      const userBubbleWrapper = document.createElement('div');
      userBubbleWrapper.className = 'message-wrapper user-wrapper';

      const userBubble = document.createElement('div');
      userBubble.className = 'message user';
      userBubble.textContent = message;
      userBubbleWrapper.appendChild(userBubble);
      chatMessagesContainer.appendChild(userBubbleWrapper);
      chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

      try {
        const response = await fetch('/send_message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: message })
        });

        if (response.ok) {
          const data = await response.json();

          if (data.error) {
            const errorBubbleWrapper = document.createElement('div');
            errorBubbleWrapper.className = 'message-wrapper bot-wrapper';
            const errorBubble = document.createElement('div');
            errorBubble.className = 'message bot';
            errorBubble.textContent = `错误: ${data.error}`;
            errorBubbleWrapper.appendChild(errorBubble);
            chatMessagesContainer.appendChild(errorBubbleWrapper);
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
          } else {
            const eventDate = new Date(data.time);
            const eventYear = eventDate.getFullYear();
            const eventMonth = eventDate.getMonth();
            const eventDay = eventDate.getDate();

            if (eventYear !== year || eventMonth !== month) {
              year = eventYear;
              month = eventMonth;
              daysInMonth = new Date(year, month + 1, 0).getDate();
              renderCalendar();
            }

            let dateEvents = highlightedDates.find(date => date.day === eventDay && date.month === eventMonth && date.year === eventYear);
            if (!dateEvents) {
              dateEvents = { year: eventYear, month: eventMonth, day: eventDay, events: [] };
              highlightedDates.push(dateEvents);
            }

            dateEvents.events.push({
              event_name: data.event_name,
              time: data.time,
              location: data.location,
              process: data.process
            });

            const dateItems = document.querySelectorAll('.date_item');
            dateItems.forEach(dateItem => {
              const date = parseInt(dateItem.textContent, 10);
              if (date === eventDay && year === eventYear && month === eventMonth) {
                dateItem.classList.add('event-day');
                dateItem.dataset.event = JSON.stringify(dateEvents.events);
              }
            });

            const botBubbleWrapper = document.createElement('div');
            botBubbleWrapper.className = 'message-wrapper bot-wrapper';
            const botBubble = document.createElement('div');
            botBubble.className = 'message bot';
            botBubble.innerHTML = `
              <strong>事件名称:</strong> ${data.event_name}<br>
              <strong>时间:</strong> ${data.time}<br>
              <strong>地点:</strong> ${data.location}<br>
              <strong>流程:</strong> ${data.process}
            `;
            botBubbleWrapper.appendChild(botBubble);
            chatMessagesContainer.appendChild(botBubbleWrapper);
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
          }
        } else {
          console.error('Error sending message to backend');
        }
      } catch (error) {
        console.error('Error:', error);
      }
    }
  });

  renderCalendar();
});

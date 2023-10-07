document.addEventListener('DOMContentLoaded', function () {
    const taskInput = document.getElementById('task');
    const addTaskButton = document.getElementById('addTask');
    const taskList = document.getElementById('taskList');

    addTaskButton.addEventListener('click', function () {
        const taskText = taskInput.value.trim();
        if (taskText !== '') {
            createTask(taskText);
            taskInput.value = '';
        }
    });

    taskInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            const taskText = taskInput.value.trim();
            if (taskText !== '') {
                createTask(taskText);
                taskInput.value = '';
            }
        }
    });

    taskList.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-button')) {
            event.target.parentElement.remove();
        }
    });

    function createTask(taskText) {
        const li = document.createElement('li');
        const emoji = document.createElement('span');
        emoji.innerText = '😃'; // You can change this emoji
        emoji.classList.add('task-text');
        li.appendChild(emoji);
        li.innerHTML += taskText;
        const deleteButton = document.createElement('button');
        deleteButton.innerText = 'Delete';
        deleteButton.classList.add('delete-button');
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    }
});

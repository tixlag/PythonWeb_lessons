const projects = [
    {
        title: "Корпоративный сайт",
        img: "https://unicoms.biz/upload/medialibrary/4d4/j4y1g05lff3bibfyhn2sidvf5f7zz3yf.jpg",
        category: "web",
        description: "Современный адаптивный сайт для IT-компании..."
    },
    {
        title: "Приложение для доставки",
        img: "https://www.ixbt.com/img/n1/news/2020/5/4/Приложение_Лавка_2_large.jpg",
        category: "mobile",
        description: "Мобильное приложение для заказа и отслеживания доставки еды"
    },
    {
        title: "Интернет-магазин",
        img: "https://avatars.mds.yandex.net/i?id=8051d2c47e508a53c7245948ec9ed368d3174af7-5213143-images-thumbs&n=13",
        category: "web",
        description: "Полнофункциональный интернет-магазин с интеграцией платежных систем"
    },
    {
        title: "Финансовое приложение",
        img: "https://avatars.mds.yandex.net/i?id=8051d2c47e508a53c7245948ec9ed368d3174af7-5213143-images-thumbs&n=13",
        category: "mobile",
        description: "Кроссплатформенное мобильное приложение для управления личными финансами"
    },
];

const portfolioGrid = document.getElementById('portfolioGrid');

function createProjectCard(project) {
    const figure = document.createElement('figure');
    figure.className = 'project-card';
    figure.dataset.category = project.category;

    const img = document.createElement('img');
    img.src = project.img;
    img.alt = `Изображение проекта: ${project.title}`;

    const figcaption = document.createElement('figcaption');
    const title = document.createElement('h3');
    title.textContent = project.title;

    const category = document.createElement('span');
    category.className = 'category';
    category.textContent = project.category;;

    const description = document.createElement('p');
    description.className = 'description';
    description.textContent = project.description;

    figcaption.append(title, category, description);
    figure.append(img, figcaption);

    return figure;
}

function renderingForAll() {
    portfolioGrid.innerHTML = '';

    projects.forEach(project => {
        const projectCard = createProjectCard(project);
        portfolioGrid.appendChild(projectCard);
    });
}

function filterProject (category) {
    const cards = document.querySelectorAll('.project-card');
    cards.forEach (card => {
        const cardCategory = card.dataset.category;
        if (category === 'all' || cardCategory === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

const filterContainer = document.querySelector('#filterControls');
filterContainer.addEventListener('click', function(event) {
    const clickedElement = event.target;
    if (clickedElement.dataset.category) {
        const selectedCategory = clickedElement.dataset.category;
        filterProject(selectedCategory);
    }
});

document.addEventListener('DOMContentLoaded', renderingForAll);
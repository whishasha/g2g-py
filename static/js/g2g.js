// general commands relevant for each user template


function hideSidenav() {
    const nav = document.querySelector('nav');
    const main = document.getElementById('main');
    
    nav.classList.toggle('hide');
    main.classList.toggle('hide');
}
"use strict";

// credit: https://www.youtube.com/watch?v=ZBJ44LrmwDI
console.log('Calendar script running.')

const datetxtEl = document.querySelector('.datetxt');
const datesEl = document.querySelector('.dates');
const btnEl = document.querySelectorAll('.calendar-headings');
const monthYearEl = document.querySelector('.month-year');



let dmObj = {
    days: [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ],
    months: [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
};


// date object
let dateObj = new Date();

//getDay returns day of the week
let dayName = dmObj.days[dateObj.getDay()]; // Gets current day in letters
let month = dateObj.getMonth(); // Gets # of current month (zero-indexed)
let year = dateObj.getFullYear(); // Gets current year
let date = dateObj.getDate(); // gets current day of the month

console.log(`The date is: ${date}/${month}/${year} `); // remove soon

datetxtEl.innerHTML = `${dayName}, ${date}, ${dmObj.months[month]}, ${year}`;

const displayCalendar = () => {
    let firstDayofMonth = new Date(year, month, 1).getDay(); // first day of current month
    let lastDateofMonth = new Date(year, month + 1, 0).getDate(); //last date of current month
    let lastDayofMonth = new Date(year, month, lastDateofMonth).getDay(); //last day of current month
    let lastDateofLastMonth = new Date(year, month, 0).getDate(); // last day of prev month
    let days = ""; //long HTML string of dates
    

    // dates must be added to align with the week
    for( let i = firstDayofMonth; i > 0; i--){
        days += `<li class="dummy date" onclick="displayDateInfo(this)">${lastDateofLastMonth - i + 1}</li>` //adds days from last month
    }
    
    for (let i = 1; i <= lastDateofMonth; i++) {
        // code which highlights SPECIFIC dates (useful for highlighting class dates)
        let checkToday = //funky if statement syntax (=== means if statement i guess)
        i === dateObj.getDate() && 
        month === new Date().getMonth() && //if statement checking if the date matches the current one
        year === new Date().getFullYear()
            ? "active date" //highlights current date
            : "date";
        


            // find a better way to add the function
        days += `<li class="${checkToday}" onclick="displayDateInfo(this)">${i}</li>`
    }

    for (let i = lastDayofMonth; i<6; i++){
        days += `<li class="dummy date" onclick="displayDateInfo(this)">${i - lastDayofMonth + 1}</li>` //adds days from next month
    }

    // display all the days of the month within the dates div
    datesEl.innerHTML = days;

    // display current month & year
    monthYearEl.innerHTML = `${dmObj.months[month]}, ${year}`;
}
displayCalendar();
const changeMonth = (El) => {
    console.log('running')
    if(El.id === "prev") {
        month -= 1;
    } else if(El.id === "next") {
        month += 1;
    }
    if (month < 0 || month > 11){
        date = new Date(year, month, new Date().getDate());
        year = date.getFullYear();
        month = date.getMonth();

    } else {
        date = new Date();
    }
    displayCalendar();
}

const dateInfoEl = document.getElementById('dateInfo');
// datesEl selects all elements with class dates

const displayDateInfo = (El) => { //need to add cases for when calendar number is too far to the left, etc.
    //event.stopPropagation();
    const offset = 200;
    var ElRect = El.getBoundingClientRect()
    console.log('banana')
    console.log(ElRect.top, ElRect.right, ElRect.bottom, ElRect.left);
    dateInfoEl.innerHTML = El.innerHTML;

    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;

    const dateInfoWidth = dateInfoEl.offsetWidth;
    const dateInfoHeight = dateInfoEl.offsetHeight;

    let leftPosition = ElRect.left + 30;
    let topPosition = ElRect.top;

    if (ElRect.left + dateInfoWidth > windowWidth) { //checking for the RIGHT 
        leftPosition -= offset;
    }
    if (ElRect.top < 0) {
        topPosition = 10
    }

    dateInfoEl.style.left = leftPosition + 'px'; //makes it APPEAR real SNAZZY!
    dateInfoEl.style.top = topPosition + 'px';
    dateInfoEl.style.display = 'relative';
}

//get list elements with class date
const dateEls = document.querySelectorAll('.date');


document.addEventListener('click', (e) => {
    if (!e.target.classList.contains('date') && !dateInfoEl.contains(e.target)) {
        dateInfoEl.style.left = '-9999px';
        dateInfoEl.style.top = '-9999px';
    }
});


// this doesn't work but idk why, fix it later ==> scuffed onclick soln implemented above
// for (var i = 0; i < dateEls.length; i++) {
//     console.log(dateEls[i])
//     dateEls[i].addEventListener("click", displayDateInfo(dateEls[i]));
// }

//the event listener isnt calling the right method
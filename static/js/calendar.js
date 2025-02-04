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
        "Febuary",
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
        days += `<li class="dummy">${lastDateofLastMonth - i + 1}</li>` //adds days from last month
    }
    
    for (let i = 1; i <= lastDateofMonth; i++) {
        
        let checkToday = //funky if statement syntax (=== means if statement i guess)
        i === dateObj.getDate() && 
        month === new Date().getMonth() && //if statement checking if the date matches the current one
        year === new Date().getFullYear()
            ? "active" //highlights current date
            : "";
        
        days += `<li class="${checkToday}">${i}</li>`
    }

    for (let i = lastDayofMonth; i<6; i++){
        days += `<li class="dummy">${i - lastDayofMonth + 1}</li>` //adds days from next month
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

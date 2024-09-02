// Function to fetch data from the Flask endpoint using the Fetch API


function fetchData(stockname) {
    //console.log(stockname)
    fetch('/stock/'+stockname+'/live')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Assuming the Flask endpoint returns JSON
        })
        .then(data => {
            // Update the HTML element with the fetched data
            //document.getElementById('data-placeholder').innerHTML = JSON.stringify(data);
           // console.log(data)

            if(data.ltp==0)
            {
                //window.location.reload(1)
            }
            previousClose=data.close
            ltp=data.ltp
            //document.getElementById(stockname).classList.remove("high")
            //document.getElementById(stockname).classList.remove("low")
            
            price_id=stockname+"_price"
            open_id=stockname+"_open"
            low_id=stockname+"_low"
            high_id=stockname+"_high"
            rsi_id=stockname+"_rsi"

            document.getElementById(price_id).classList.remove("high")
            document.getElementById(price_id).classList.remove("low")

            if(ltp>previousClose)
            {
                document.getElementById(price_id).classList.add("high")
            }
                //document.getElementById(stockname).classList.add("high")
                //document.getElementById(price_id).classList.add("high")

            if(ltp<previousClose)
            {
                document.getElementById(price_id).classList.add("low")
            }
                //document.getElementById(stockname).classList.add("low")
                //document.getElementById(price_id).classList.add("low")

            //document.getElementById(stockname).innerHTML=data.ltp

            //document.getElementById(stockname).innerHTML=stockname+" - "+data.ltp
            document.getElementById(price_id).innerHTML=data.ltp
            document.getElementById(open_id).innerHTML=data.open
            document.getElementById(low_id).innerHTML=data.low
            document.getElementById(high_id).innerHTML=data.high
            document.getElementById(rsi_id).innerHTML=data.rsi
            //console.log("Fetched")
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Call fetchData every 5 seconds (5000 milliseconds)
stockList=document.getElementById("stocklist").value
//console.log(stockList)
// Parse the string as a JSON array
const array = JSON.parse(stockList.replace(/'/g, '"')); // Replacing single quotes with double quotes for valid JSON

// Loop through the array and log each value
array.forEach(value => {
    //console.log(value)
    interval=Math.floor(Math.random() * 5000) + 5000
    setInterval(function() { fetchData(value); },interval );
});





// Optionally, fetch data immediately when the page loads
//document.addEventListener('DOMContentLoaded', fetchData);
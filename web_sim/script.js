  class Slider {
    constructor (rangeElement, valueElement, options, microgam=false) {
      this.rangeElement = rangeElement
      this.valueElement = valueElement
      this.options = options
      this.microgam = microgam
  
      // Attach a listener to "change" event
      this.rangeElement.addEventListener('input', this.updateSlider.bind(this))
    }
  
    // Initialize the slider
    init() {
      this.rangeElement.setAttribute('min', this.options.min)
      this.rangeElement.setAttribute('max', this.options.max)
      this.rangeElement.value = this.options.cur
  
      this.updateSlider()
    }
  
    // Format the money
    asppm(value) {
      return parseFloat(value)
        .toLocaleString('en-US', { maximumFractionDigits: 2 }) + " ppm"
    }

    asmicrogam(value){
        return parseFloat(value)
        .toLocaleString('en-US', { maximumFractionDigits: 7 }) + " µg/cm3"
    }
  
    generateBackground(rangeElement) {   
      if (this.rangeElement.value === this.options.min) {
        return
      }
  
      let percentage =  (this.rangeElement.value - this.options.min) / (this.options.max - this.options.min) * 100
      return 'background: linear-gradient(to right, #3aff02, #ff0000 ' + percentage + '%, #d3edff ' + percentage + '%, #dee1e2 100%)'
    }
  
    updateSlider (newValue) {
      this.valueElement.innerHTML = this.asppm(this.rangeElement.value)
      if (this.microgam){
        this.valueElement.innerHTML = this.asmicrogam(this.rangeElement.value)
      } else {
        this.valueElement.innerHTML = this.asppm(this.rangeElement.value)
      }
      this.rangeElement.style = this.generateBackground(this.rangeElement.value)
    }
  }

  function myTimer(co, no2, o3, pm25) {
    const date = new Date();
    document.getElementById("demo").innerHTML = date.toLocaleTimeString();

    var data = JSON.stringify({
      "co": parseFloat(co.value),
      "no2": parseFloat(no2.value),
      "o3": parseFloat(o3.value),
      "pm25": parseFloat(pm25.value)
    })
    console.log(data.toLocaleString())

    let xhr = new XMLHttpRequest()
    xhr.open("POST", "http://localhost:8000/lora_api/", true)
    xhr.setRequestHeader("Content-Type", "application/json")
    xhr.setRequestHeader("accept", "application/json")
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
          console.log(this.responseText)
      }
    }
    xhr.send(data)

  }
  
  let rangeElementCO = document.querySelector('#co [type="range"]')
  let valueElementCO = document.querySelector('#co .range__value span') 

  let rangeElementNO2 = document.querySelector('#no2 [type="range"]')
  let valueElementNO2 = document.querySelector('#no2 .range__value span') 

  let rangeElementO3 = document.querySelector('#o3 [type="range"]')
  let valueElementO3 = document.querySelector('#o3 .range__value span') 

  let rangeElementPM25 = document.querySelector('#pm25 [type="range"]')
  let valueElementPM25 = document.querySelector('#pm25 .range__value span') 
  
  let optionsCO = {
    min: 0,
    max: 2000,
    cur: 100
  }
  let optionsNO2 = {
    min: 0,
    max: 200,
    cur: 50
  }
  let optionsO3 = {
    min: 0,
    max: 2,
    cur: 0.5
  }
  let optionsPM25 = {
    min: 0,
    max: 1e-4,
    cur: 4e-5
  }
  
  if (rangeElementCO) {
    let sliderCO = new Slider(rangeElementCO, valueElementCO, optionsCO) 
    sliderCO.init()
  }
  if (rangeElementNO2) {
    let sliderNO2 = new Slider(rangeElementNO2, valueElementNO2, optionsNO2) 
    sliderNO2.init()
  }
  if (rangeElementO3) {
    let sliderO3 = new Slider(rangeElementO3, valueElementO3, optionsO3) 
    sliderO3.init()
  }
  if (rangeElementPM25) {
    let sliderPM25 = new Slider(rangeElementPM25, valueElementPM25, optionsPM25, microgam=true) 
    sliderPM25.init()
  }

  setInterval(myTimer, 10000, rangeElementCO, rangeElementNO2, rangeElementO3, rangeElementPM25);

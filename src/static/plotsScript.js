const PLOT_WIDTH = 600;
const PLOT_HEIGHT = 700
function getSundayFromWeekNum(year,weekNum) {
    var monday = new Date(year, 0, (1 + (weekNum - 1) * 7));
	monday.setDate(monday.getDate() + (1-monday.getDay()));
    return monday;
}
function getWeeklyData() {
	const year_week = document.getElementById("week").value;
	
	const year = parseFloat(year_week)
	console.log(year_week)
	const week_num = parseFloat(year_week.slice(6,8))
	const week = getSundayFromWeekNum(parseFloat(year_week),parseFloat(week_num));
	console.log(week)
    const url = 'http://127.0.0.1:5000/me/weekly_data?start_date=' + week.getTime()
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            distance_data = json['data']
            console.log(distance_data)
            var data = [
                {
                    x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    y: distance_data,
                    type: 'bar',
                    text: distance_data.map(String),
                    marker: {
                        color: 'rgb(255,0,0)',
                        opacity: 0.5
                    }
                }
            ];
            var layout = {
				autosize: true,
                title: 'Distance per day',
                xaxis: {
                    title: 'Day'
                },
                yaxis: {
                    title: 'Distance(km)'
                },
				width: PLOT_WIDTH*3
            }
			var config = {responsive: true}

            Plotly.newPlot('weeklyPlot', data, layout,config);
        })
}
function getYearlyData() {
	const div = document.getElementById("activityType");
	url = `http://127.0.0.1:5000/me/yearly_data`
	if(div !== null){
		const type = div.value;
		console.log(type);
		url = `http://127.0.0.1:5000/me/yearly_data?type=${type}`
	}
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            distance_data = json['data']
            console.log(distance_data)
            datas = []
            colors = ['rgba(67,67,67,1)', 'rgba(115,115,115,1)', 'rgba(49,130,189, 1)', 'rgba(189,189,189,1)']
            for (let i = 0; i < distance_data.length; i++) {
                var data = {
                    //	x: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                    x: Array.from(Array(365).keys()),
                    y: distance_data[i],
                    type: 'scatter',
                    mode: 'lines',
                    name: String(2020 + i),
                    text: distance_data[i].map(String),
                    marker: {
                        color: 'rgb(255,0,0)',
                        opacity: 0.5
                    },
                    line: {
                        color: colors[i]
                    }
                };
                datas.push(data);
                console.log(data)
            }
            console.log(datas)
            var layout = {
                title: 'Distance per year',
                xaxis: {
                    title: 'Day'
                },
                yaxis: {
                    title: 'Distance(km)'
                },
				width: PLOT_WIDTH*1.5,
            }

            Plotly.newPlot('yearlyPlot', datas, layout);
        })
}

function getPieCountData() {
    const url = 'http://127.0.0.1:5000/me/pie_data_count';
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            let types = json.map(activity => activity.type);
            let counts = json.map(activity => activity.count);

            var data = [{
                values: counts,
                labels: types,
                type: 'pie',
                textinfo: 'label+percent',
                automargin: true
            }];

            var layout = {
                title: 'number of times each activity has been done',
                height: PLOT_HEIGHT,
                width: PLOT_WIDTH,
                showlegend: true
            };

            Plotly.newPlot('piePlot', data, layout);
        });
}

function getPieDataTime() {
    const url = 'http://127.0.0.1:5000/me/pie_data_time';
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            let types = json.map(activity => activity.type);
            let times = json.map(activity => activity.time);

            var data = [{
                values: times,
                labels: types,
                type: 'pie',
                hoverinfo: 'label+percent+name',
                textinfo: 'label+value',
                textposition: 'outside',
                automargin: true
            }];

            var layout = {
                title: 'time spent doing each activty type (hours)',
                height: PLOT_HEIGHT,
                width: PLOT_WIDTH,
                showlegend: true
            };

            Plotly.newPlot('piePlotTime', data, layout);
        })
}

function getPieDataDistance() {
    const url = 'http://127.0.0.1:5000/me/pie_data_distance';
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            let types = json.map(activity => activity.type);
            let distances = json.map(activity => activity.distance);

            var data = [{
                values: distances,
                labels: types,
                type: 'pie',
                hoverinfo: 'label+percent+name',
                textinfo: 'label+value',
                textposition: 'outside',
                automargin: true
            }];

            var layout = {
                title: 'total distance completed of each activity type (km)',
                height: PLOT_HEIGHT,
                width: PLOT_WIDTH,
                showlegend: true
            };

            Plotly.newPlot('pieDistance', data, layout);
        })
}

function getYearlyKudos() {
    const url = 'http://127.0.0.1:5000/me/yearly_kudos'; 
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            kudos_data = json['data'];
            console.log(kudos_data);
            datas = [];
            colors = ['rgba(67,67,67,1)', 'rgba(115,115,115,1)', 'rgba(49,130,189, 1)', 'rgba(189,189,189,1)'];
            for (let i = 0; i < kudos_data.length; i++) {
                var data = {
                    x: Array.from(Array(365).keys()),
                    y: kudos_data[i],
                    type: 'scatter',
                    mode: 'lines',
                    name: String(2020 + i), 
                    text: kudos_data[i].map(String),
                    marker: {
                        color: 'rgb(255,165,0)',
                        opacity: 0.5
                    },
                    line: {
                        color: colors[i]
                    }
                };
                datas.push(data);
                console.log(data);
            }
            console.log(datas);
            var layout = {
                title: 'annual cumulative kudos',
                xaxis: {
                    title: 'day of year'
                },
                yaxis: {
                    title: 'kudos'
                },
				width: PLOT_WIDTH*1.5,
            };

            Plotly.newPlot('yearlyPlotKudos', datas, layout);
        })
}

function getYearlyElevation() {
	const div = document.getElementById("activityType");
	url = `http://127.0.0.1:5000/me/yearly_data_elev`
	if(div !== null){
		const type = div.value;
		console.log(type);
		url = `http://127.0.0.1:5000/me/yearly_data_elev?type=${type}`
	}
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            elev_data = json['data']
            console.log(elev_data)
            datas = []
            colors = ['rgba(67,67,67,1)', 'rgba(115,115,115,1)', 'rgba(49,130,189, 1)', 'rgba(189,189,189,1)']
            for (let i = 0; i < elev_data.length; i++) {
                var data = {
                    //	x: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                    x: Array.from(Array(365).keys()),
                    y: elev_data[i],
                    type: 'scatter',
                    mode: 'lines',
                    name: String(2020 + i),
                    text: elev_data[i].map(String),
                    marker: {
                        color: 'rgb(255,0,0)',
                        opacity: 0.5
                    },
                    line: {
                        color: colors[i]
                    }
                };
                datas.push(data);
                console.log(data)
            }
            console.log(datas)
            var layout = {
                title: 'cumulative elevation gain per year',
                xaxis: {
                    title: 'Day'
                },
                yaxis: {
                    title: 'Elevation gain (m)'
                },
				width: PLOT_WIDTH*1.5,
            }

            Plotly.newPlot('yearlyPlotElev', datas, layout);
        })
}

function getUserInfo() {
    const url = 'http://127.0.0.1:5000/me/user_info'
    fetch(url)
        .then(response => response.json())  
        .then(json => {
            console.log(json)
            const welcomename = document.getElementById('welcomename')
            welcomename.textContent = 'Welcome, ' + json.firstname;
        });
}

function getYearlyTime() {
    const url = 'http://127.0.0.1:5000/me/annual_cumulative_time'
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            time_data = json['data']
            console.log(time_data)
            datas = []
            colors = ['rgba(67,67,67,1)', 'rgba(115,115,115,1)', 'rgba(49,130,189, 1)', 'rgba(189,189,189,1)']
            for (let i = 0; i < time_data.length; i++) {
                var data = {
                    //	x: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                    x: Array.from(Array(365).keys()),
                    y: time_data[i],
                    type: 'scatter',
                    mode: 'lines',
                    name: String(2020 + i),
                    text: time_data[i].map(String),
                    marker: {
                        color: 'rgb(255,0,0)',
                        opacity: 0.5
                    },
                    line: {
                        color: colors[i]
                    }
                };
                datas.push(data);
                console.log(data)
            }
            console.log(datas)
            var layout = {
                title: 'annual cumulative time',
                xaxis: {
                    title: 'Day'
                },
                yaxis: {
                    title: 'time(hours)'
                },
				width: PLOT_WIDTH*1.5,
            }

            Plotly.newPlot('yearlyTime', datas, layout);
        })
}


function getPieDataElevation() {
    const url = 'http://127.0.0.1:5000/me/pie_data_elevation';
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            let types = json.map(activity => activity.type);
            let distances = json.map(activity => activity.distance);

            var data = [{
                values: distances,
                labels: types,
                type: 'pie',
                hoverinfo: 'label+percent+name',
                textinfo: 'label+value',
                textposition: 'outside',
                automargin: true
            }];

            var layout = {
                title: 'total elevation completed of each activity type (m)',
                height: PLOT_HEIGHT,
                width: PLOT_WIDTH,
                showlegend: true
            };

            Plotly.newPlot('pieElevation', data, layout);
        })
}

function getAlltimeDist() {
    const url = 'http://127.0.0.1:5000/me/alltime_dist'
    fetch(url)
        .then(response => response.json())  
        .then(json => {
            console.log(json)
            const totaldist = document.getElementById('totaldist')
            totaldist.textContent = 'Alltime all activity total distance: ' + json.distance;
        });
}

function getYearlyDataAct() {
    const activityType = document.getElementById('activityType').value;
    const url = `http://127.0.0.1:5000/me/yearly_data_activity?activity_type=${activityType}`;

    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            const distance_data = json['data'];
            console.log(distance_data);
            const datas = [];
            const colors = ['rgba(67,67,67,1)', 'rgba(115,115,115,1)', 'rgba(49,130,189, 1)', 'rgba(189,189,189,1)'];
            for (let i = 0; i < distance_data.length; i++) {
                var data = {
                    x: Array.from(Array(365).keys()),
                    y: distance_data[i],
                    type: 'scatter',
                    mode: 'lines',
                    name: String(2020 + i),
                    text: distance_data[i].map(String),
                    marker: {
                        color: 'rgb(255,0,0)',
                        opacity: 0.5
                    },
                    line: {
                        color: colors[i]
                    }
                };
                datas.push(data);
                console.log(data);
            }
            console.log(datas);
            var layout = {
                title: 'Distance per year',
                xaxis: {
                    title: 'Day'
                },
                yaxis: {
                    title: 'Distance(km)'
                }
            };

            Plotly.newPlot('yearlyPlotAct', datas, layout);
        });
}

function getPieKudos() {
    const url = 'http://127.0.0.1:5000/me/pie_data_kudos';
    fetch(url) 
        .then(response => response.json())
        .then(json => {
            console.log(json);
            let types = json.map(activity => activity.type);
            let kudosData = json.map(activity => activity.kudos);

            var data = [{
                values: kudosData,
                labels: types,
                type: 'pie',
                hoverinfo: 'label+percent+name',
                textinfo: 'label+value',
                textposition: 'outside',
                automargin: true
            }];

            var layout = {
                title: 'total kudos accumulated of each activity type',
                height: PLOT_HEIGHT,
                width: PLOT_WIDTH,
                showlegend: true
            };

            Plotly.newPlot('pieKudos', data, layout);
        })
}

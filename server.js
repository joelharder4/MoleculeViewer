
function onSubmit() {
    let inputSDF = document.querySelector("input[type=file]").files[0];
    let inputText = document.getElementById("nameTag").value;
    
    if (inputSDF == null) {
        alert("no file selected");
        return;
    }
    if (inputText == "" || inputText.includes(';')) {
        alert("invalid name");
        return;
    }


    let fileReader = new FileReader();

    fileReader.onload = function() {
        $.post("../molecule/" + inputSDF.name, {
            name: inputText,
            file: fileReader.result
        },
        function( data, status )
        {
            window.location.replace("/molecules");
        }
        );
    }; 

    fileReader.readAsText(inputSDF);
    
    fileReader.onerror = function() {
        alert(fileReader.error);
    };
}



function isNumeric(str) {
    return /^\d+$/.test(str);
}

function hasNumber(myString) {
    return /\d/.test(myString);
}



function addElement() {
    let name = document.getElementById("nameTag").value;
    let code = document.getElementById("codeTag").value;
    let number = document.getElementById("numberTag").value;
    let radius = document.getElementById("radiusTag").value;
    let colour1 = document.getElementById("colour1Tag").value;
    let colour2 = document.getElementById("colour2Tag").value;
    let colour3 = document.getElementById("colour3Tag").value;

    if (hasNumber(name) == true || name == "" || name.includes(';')) {
        alert("Invalid element name");
        return;
    }
    if (hasNumber(code) == true || code == "" || code.includes(';')) {
        alert("Invalid element code");
        return;
    }
    if (isNumeric(number) == false || number == "") {
        alert("Invalid element number");
        return;
    }
    if (isNumeric(radius) == false || radius == "") {
        alert("Invalid radius");
        return;
    } else if (parseInt(radius) > 100 || parseInt(radius) < 20) {
        alert("radius must be at least 20 and at most 100");
        return;
    }
    if (colour1.length != 6) {
        alert("Invalid colour1");
        return;
    }
    if (colour2.length != 6) {
        alert("Invalid colour2");
        return;
    }
    if (colour3.length != 6) {
        alert("Invalid colour3");
        return;
    }
    
    $.post("../element/" + name, {
        name: name,
        code: code,
        number: number,
        radius: radius,
        colour1: colour1,
        colour2: colour2,
        colour3: colour3
    },
    function( data, status )
    {
        console.log("Data: " + data + "\nStatus: " + status);
        window.location.replace("/elements");
    }
    );
}


function onRotate() {
    let roll = document.getElementById("rollTag").value;
    let pitch = document.getElementById("pitchTag").value;
    let yaw = document.getElementById("yawTag").value;

    if (isNumeric(roll) == false) {
        alert("Invalid Roll. It must be a number in degrees.");
        return;
    } else if (parseInt(roll) > 360 || parseInt(roll) < 0) {
        alert("Invalid Roll. A valid rotation must be between 0 and 360 degrees.");
        return;
    }
    if (isNumeric(pitch) == false) {
        alert("Invalid Pitch. It must be a number in degrees.");
        return;
    } else if (parseInt(pitch) > 360 || parseInt(pitch) < 0) {
        alert("Invalid Pitch. A valid rotation must be between 0 and 360 degrees.");
        return;
    }
    if (isNumeric(yaw) == false) {
        alert("Invalid Yaw. It must be a number in degrees.");
        return;
    } else if (parseInt(yaw) > 360 || parseInt(yaw) < 0) {
        alert("Invalid Yaw. A valid rotation must be between 0 and 360 degrees.");
        return;
    }
    

    let split = window.location.href.split('/');
    let molname = split.slice(-1);
    $.post("../view/" + molname, {
        roll: roll,
        pitch: pitch,
        yaw: yaw
    },
    function( data, status )
    {
        console.log("Data: " + data + "\nStatus: " + status);

        div = document.getElementById("svgHolder");
        div.innerHTML = data;
    }
    );
}



// function sleep(milliseconds) {
//     const date = Date.now();
//     let currentDate = null;
//     do {
//       currentDate = Date.now();
//     } while (currentDate - date < milliseconds);
// }

const index = 0;


function onSpin() {
    let split = window.location.href.split('/');
    let molname = split.slice(-1);
    $.post("../spin/" + molname, {
        name: molname
    },
    function( data, status )
    {
        let div = document.getElementById("svgHolder");

        function setFrame( data, index) {
            div.innerHTML = data[index];

            if (index < 359) {
                setTimeout(setFrame, 50, data, index+1);
            }
        }

        setTimeout(setFrame, 50, data, 0);
    }
    );
}



function onUpload() {
    let inputSDF = document.querySelector("input[type=file]").files[0];
    let sdfName = document.getElementById("sdfName");
    sdfName.innerText = inputSDF.name;
}


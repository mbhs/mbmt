function request(url) {
    return new Promise(function(resolve, reject) {
        var request = new XMLHttpRequest();
        request.open("GET", url, true);
        request.onreadystatechange = function() {
            if (this.state < 200 || this.status >= 300)
                reject({staus: this.status, statusText: this.statusText});
            else if (this.readyState == 4) {
                console.log(this.responseText);
                resolve(JSON.parse(this.responseText));
            }
        };
        this.onerror = function() {
            reject({status: this.status, statusText: this.statusText});
        };
        request.send();
    });
}

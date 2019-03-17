'use strict'

// let updated = Date.now()
let updated = '1552805662657'

/**
 * Module dependencies.
 */

const https = require('https')
const fs = require('fs')
const { exec } = require('child_process')

function download (url, dest, cb) {
  let file = fs.createWriteStream(dest)
  let request = https.get(url, function (response) {
    response.pipe(file)
    file.on('finish', function () {
      file.close(cb) // close() is async, call cb after close completes.
    })
  }).on('error', function (err) { // Handle errors
    fs.unlink(dest) // Delete the file async. (But we don't check the result)
    if (cb) cb(err.message)
  })
}

/**
 * Scan node_modules directory for vulnerabilities.
 * Supports promises, allowing heuristics with longer processes
 * like HTTP requests to run in parallel.
 */

function scan () {
  https.get(`https://skimdb.npmjs.com/registry/_design/app/_list/index/modified?startkey=${updated}`, (response) => {
    if (response.status >= 400) {
      console.error(`Request to ${response.url} failed with HTTP ${response.status}`)
    }

    var body = ''

    response.on('data', (chunk) => {
      body += chunk.toString()
    })

    response.on('end', () => {
      let data = JSON.parse(body)
      updated = data._updated
      console.log(updated)

      for (const packageName in data) {
        if (packageName !== '_updated') {
          exec(`npm v ${packageName}@latest dist.tarball`, (err, stdout) => {
            if (err) {
              return
            }
            let fileName = `${packageName}-${data[packageName]['dist-tags'].latest}.tgz`
            console.log(fileName)
            fs.mkdirSync(`packages/${data._updated}`, { recursive: true });
            download(stdout, `packages/${data._updated}/${fileName}`)
          })
        }
      }
    })
  })
}

/**
 * Scan node_modules directory for vulnerabilities.
 * Supports promises, allowing heuristics with longer processes
 * like HTTP requests to run in parallel.
 */

function main () {
  setInterval(scan, 5000)
}

main()

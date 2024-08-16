# Website Watcher

A simple script that uses Github Actions and [ntfy.sh](https://ntfy.sh/) to periodically poll websites and notify you when they change -- for free. You can be notified when the site adds/removes a string or changes content.

Note: it does not support dynamically generated sites, as it only compares the HTML it receives.

## Get started
1. Fork this repository.

2. Go to the repo's settings > Actions > Workflow permissions and set to `Read and write permissions`.

3. Set your [ntfy.sh topic name](https://docs.ntfy.sh/) as a [repository secret](https://docs.github.com/es/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) with name the `NTFY_TOPIC`.

4. Edit `.github/workflows/poll-websites` line 6 with the cron schedule expression of your preference. Default is `"0 6 * * *"` (daily at 6 am).

4. Edit `watch.json`.


## watch.json

You can specify which websites to poll and under what conditions the script should notify you in `watch.json`. 

The file consists of a list of key-value pairs. 
You specify the name of each website / notification as the key of an entry. This is the name that will appear in notifications.
The value of each key must be another object and contain at least:

- `"url"`: the url to monitor (with GET requests)
- `"on"`: the criteria that will trigger a notification. `"in"` will notify if the text in `"txt"` is in the retried HTML, `"not_in"` the opposite, and `"change"` will do so if the page changes from a cached version. 

You must include a `"txt"` field if `"on"` is either `"in"` or `"not_in"`.

Note: `"change"` will automatically cache the page the first time the script is ran and will overwrites cached version when a change is detected.
# Platform Scripts

## What's the purpose of this repository?

To have a centralised place for all random miscellaneous platform scripts to be stored for potental future use

## How to Work with this Repo

If you are adding a new script, please create a new folder for your script, then add your script in the folder preferably along with a short readme talking about your script, so that other engineers can understand what it does!

### Using uv

Working with uv allows us to easily work with scripts. If you have uv installed you can run the following to install dependencies for a specific script:

```
uv add --script <path/to/script> 'dep1' 'dep2'
```

This will modify the script and a special comment to the top with a list of dependencies and python version. Python version can be forced with a `.python-version` file in the subfolder. Then, at runtime, uv will install and cache these dependencies and run the script blazingly fast.

You can use `uv run <path/to/script>` from here to run the script. Alternatively, you can add the following shebang to the top of the file:

```
#!/usr/bin/env -S uv run --quiet
```

and then run

```
chmod 755 <path/to/script>
```

in order to run the script with just 
```
./<path/to/script>
```
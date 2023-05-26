# FlapGenerator

Using this tool you can create a BGP peer who is announcing some routes where a subset of this routes is flapping.
The real magic (the BGP session) is done by [ExaBGP](https://github.com/Exa-Networks/exabgp) this tool just provides
a script to instruct ExaBGP to announce and withdraw the routes.

## Installation
Starting your flapping peer is just a git clone and the setup of a python venv away:

```bash
git clone https://github.com/marcelb98/flapgenerator.git
cd flapgenerator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

(This installs ExaBGP from PIP, so you don't have to install it in some other way.)

## Usage
### 1. Create a setup
To do as much work as possible before starting the BGP session,
the list of announced and flapping prefixes is created in advance.

Just run `flapgenerator.py routeflap` to generate a setup.json.
See `flapgenerator.py routeflap --help` for all options.

The tool can create IPv4 routes (/32) and IPv6 routes (/64 subnets).

The generated setup will be stored as `/tmp/flapgenerator_setup.json`.
If you need some kind of special setup, you can also create this JSON on your own and store it at this location.

### 2. Configure ExaBGP
To setup the peering you need to configure the ExaBGP configuration (`exa.config`).
Especially the neighbor configuration needs to be changed to your needs.
Just make sure to add the

```json
api {
  processes [announce-routes];
}
```

block to each neighbor you want to send routes (including the flapping ones) to.

### 3. Run ExaBGP
Start ExaBGP by running `exabgp ./exa.config`.

### 4. Profit

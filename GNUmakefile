### https://tech.davis-hansson.com/p/make/
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -o errexit -o nounset -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
.RECIPEPREFIX = >
###

.PHONY: clean
clean:
> rm -rf .venv venv

### PYTHON ENVIRONMENT BUILDING

python_version := 3.7

global_python := python${python_version}
venv_target := venv
venv_dir := .venv
venv_bin := ${venv_dir}/bin
venv_python := ${venv_bin}/python${python_version}

requirements.txt: requirements.in
> pip-compile \
>   --quiet \
>   --generate-hashes \
>   --no-index \
>   --output-file=$@ \
>   $<
> chmod 644 $@  # strange permissions sometimes...

# ${venv_target}: requirements.txt
${venv_target}:
> if [ -d "${venv_dir}" ]; then
>   # kinda hacky, but can be much faster than the full rebuild
>   ${venv_dir}/bin/pip install pip-tools
>   ${venv_dir}/bin/pip-sync
>   ${venv_dir}/bin/pip uninstall -y pip-tools
> else
>   rm -rf "${venv_dir}"
>   ${global_python} -m venv ${venv_dir}
>   ${venv_python} -m pip install \
>     --disable-pip-version-check \
>     --no-deps \
>     --require-hashes \
>     --requirement requirements.txt
>   ${venv_python} -m pip list > ${venv_target}
> fi

REGISTRY=$1
ORG=$2

echo "\n LOGIN \n"
docker login $REGISTRY -u $3 --password $4

TAG=`git describe --tags $(git rev-list --tags --max-count=1)`

COMMIT=`git rev-parse HEAD`

cat dockerfile_template \
 | sed "s/{git_commit}/$COMMIT/g" \
 > dockerfile

docker build -t mtorreslworks/single_cell_pipeline_hmmcopy:v0.8.14.mod . --no-cache

docker push mtorreslworks/single_cell_pipeline_hmmcopy:v0.8.14.mod


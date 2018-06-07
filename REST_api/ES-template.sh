curl -XPOST 'http://atlas-kibana.mwt2.org:9200/_template/cost_matrix' -d '{
    "index_patterns" : "cost_matrix",
    "settings" : {
        "number_of_shards" : 5,
        "number_of_replicas" : 1
    },
    "mappings" : {
        "docs" : {
            "_source" : { "enabled" : true },
            "properties" : {
                "destination" : { "type" : "keyword" },
                "source" : { "type" : "keyword" },
                "log" : { "type" : "keyword" },
                "rate" : { "type" : "float" },
                "last" : { "type" : "boolean" },
                "timestamp" : { "type" : "date" }
            }
        }
    }
}'
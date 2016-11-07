class Api {
    category: string;
    types: string[];
    limit: number;
    offset: number;
    sort: string;
    result: {};
    constructor(types: string[]){
      this.limit = 12;
      this.offset = 0;
      this.types = types;
    }
    fetch(){
      $.getJSON("http://localhost:9200/shop/products/", {type: this.types}
        res => {this.result = res;});
      }
}

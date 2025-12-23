# 免费多维表格 [NocoDB](https://nocodb.com/)

## Account

- UserID：usstum133iefy143
- [Dashboard](https://app.nocodb.com/)
- API Token <PASSWORD>

```PASSWORD
// API Token: 
1sqIAdEVPYiX0NSg954kQS9VhvJ3A4-kZJXSgtuU
```

##  Table Project-1: timeline-story
    - ID: vw78qlqx4dqak55v
    - Name: `timeline-story-js`

### Title:


||Field Name	|Field Type	|Description|
|:--|:-------------|:--------------|:------------------------:|
|1|id	|Auto-number	|Event ID (auto-generated)|
|2|year	|Number	|From start_date.year.|
|3|headline	|Single-line text	|From text.headline.|
|4|text	|Long text	|From text.text.|
|5|media.url	|URL (single link)	|From media.url.|
|6|media.caption	|Long text	|From media.caption.|
|7|media.credit	|Single-line text	|From media.credit.|
|8|media.link	|URL (single link)	|From media.link.|
|9|title.headline	|Single-line text	|Project main headline from title.text.headline (excluding SVG).
|10|title.text	|Single-line text	|Project subtitle from title.text.text.|
|11|title.media.url	|URL (single link)	|From title.media.url.|
|12|title.media.caption	|Long text	From |title.media.caption.|
|13|title.media.credit	|Single-line text	|From title.media.credit.|

### Script example

#### JavaScript

**Fatch data from NocoDB API**
```javascript
const options = {
	method: 'GET',
	headers: {
		'xc-token': 'CREATE_YOUR_API_TOKEN_FROM https://app.nocodb.com/#/account/tokens'
	}
};

fetch('https://app.nocodb.com/api/v2/tables/mwwjl1scwot3l4f/records?offset=0&limit=25&where=&viewId=vw78qlqx4dqak55v', options)
	.then(res => res.json())
	.then(res => console.log(res))
	.catch(err => console.error(err));
```
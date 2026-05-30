const L=globalThis,K=L.ShadowRoot&&(L.ShadyCSS===void 0||L.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Z=Symbol(),X=new WeakMap;let he=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==Z)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(K&&e===void 0){const i=t!==void 0&&t.length===1;i&&(e=X.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&X.set(t,e))}return e}toString(){return this.cssText}};const we=r=>new he(typeof r=="string"?r:r+"",void 0,Z),Se=(r,...e)=>{const t=r.length===1?r[0]:e.reduce((i,s,n)=>i+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+r[n+1],r[0]);return new he(t,r,Z)},Ee=(r,e)=>{if(K)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const i=document.createElement("style"),s=L.litNonce;s!==void 0&&i.setAttribute("nonce",s),i.textContent=t.cssText,r.appendChild(i)}},Y=K?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return we(t)})(r):r;const{is:xe,defineProperty:Ce,getOwnPropertyDescriptor:Ie,getOwnPropertyNames:Re,getOwnPropertySymbols:Pe,getPrototypeOf:Ne}=Object,_=globalThis,ee=_.trustedTypes,Oe=ee?ee.emptyScript:"",Me=_.reactiveElementPolyfillSupport,x=(r,e)=>r,W={toAttribute(r,e){switch(e){case Boolean:r=r?Oe:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},pe=(r,e)=>!xe(r,e),te={attribute:!0,type:String,converter:W,reflect:!1,useDefault:!1,hasChanged:pe};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),_.litPropertyMetadata??(_.litPropertyMetadata=new WeakMap);let b=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??(this.l=[])).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=te){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(e,i,t);s!==void 0&&Ce(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){const{get:s,set:n}=Ie(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:s,set(o){const l=s?.call(this);n?.call(this,o),this.requestUpdate(e,l,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??te}static _$Ei(){if(this.hasOwnProperty(x("elementProperties")))return;const e=Ne(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(x("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(x("properties"))){const t=this.properties,i=[...Re(t),...Pe(t)];for(const s of i)this.createProperty(s,t[s])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[i,s]of t)this.elementProperties.set(i,s)}this._$Eh=new Map;for(const[t,i]of this.elementProperties){const s=this._$Eu(t,i);s!==void 0&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const s of i)t.unshift(Y(s))}else e!==void 0&&t.push(Y(e));return t}static _$Eu(e,t){const i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??(this._$EO=new Set)).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ee(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(s!==void 0&&i.reflect===!0){const n=(i.converter?.toAttribute!==void 0?i.converter:W).toAttribute(t,i.type);this._$Em=e,n==null?this.removeAttribute(s):this.setAttribute(s,n),this._$Em=null}}_$AK(e,t){const i=this.constructor,s=i._$Eh.get(e);if(s!==void 0&&this._$Em!==s){const n=i.getPropertyOptions(s),o=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:W;this._$Em=s;const l=o.fromAttribute(t,n.type);this[s]=l??this._$Ej?.get(s)??l,this._$Em=null}}requestUpdate(e,t,i,s=!1,n){if(e!==void 0){const o=this.constructor;if(s===!1&&(n=this[e]),i??(i=o.getPropertyOptions(e)),!((i.hasChanged??pe)(n,t)||i.useDefault&&i.reflect&&n===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,i))))return;this.C(e,t,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:n},o){i&&!(this._$Ej??(this._$Ej=new Map)).has(e)&&(this._$Ej.set(e,o??t??this[e]),n!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),s===!0&&this._$Em!==e&&(this._$Eq??(this._$Eq=new Set)).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(const[s,n]of this._$Ep)this[s]=n;this._$Ep=void 0}const i=this.constructor.elementProperties;if(i.size>0)for(const[s,n]of i){const{wrapped:o}=n,l=this[s];o!==!0||this._$AL.has(s)||l===void 0||this.C(s,void 0,n,l)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(t)):this._$EM()}catch(i){throw e=!1,this._$EM(),i}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&(this._$Eq=this._$Eq.forEach(t=>this._$ET(t,this[t]))),this._$EM()}updated(e){}firstUpdated(e){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[x("elementProperties")]=new Map,b[x("finalized")]=new Map,Me?.({ReactiveElement:b}),(_.reactiveElementVersions??(_.reactiveElementVersions=[])).push("2.1.2");const C=globalThis,ie=r=>r,H=C.trustedTypes,re=H?H.createPolicy("lit-html",{createHTML:r=>r}):void 0,me="$lit$",g=`lit$${Math.random().toFixed(9).slice(2)}$`,fe="?"+g,ke=`<${fe}>`,y=document,P=()=>y.createComment(""),N=r=>r===null||typeof r!="object"&&typeof r!="function",J=Array.isArray,Ue=r=>J(r)||typeof r?.[Symbol.iterator]=="function",B=`[ 	
\f\r]`,E=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,se=/-->/g,ne=/>/g,$=RegExp(`>|${B}(?:([^\\s"'>=/]+)(${B}*=${B}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),oe=/'/g,ae=/"/g,ge=/^(?:script|style|textarea|title)$/i,Te=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),p=Te(1),w=Symbol.for("lit-noChange"),c=Symbol.for("lit-nothing"),le=new WeakMap,v=y.createTreeWalker(y,129);function _e(r,e){if(!J(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return re!==void 0?re.createHTML(e):e}const Le=(r,e)=>{const t=r.length-1,i=[];let s,n=e===2?"<svg>":e===3?"<math>":"",o=E;for(let l=0;l<t;l++){const a=r[l];let d,h,u=-1,m=0;for(;m<a.length&&(o.lastIndex=m,h=o.exec(a),h!==null);)m=o.lastIndex,o===E?h[1]==="!--"?o=se:h[1]!==void 0?o=ne:h[2]!==void 0?(ge.test(h[2])&&(s=RegExp("</"+h[2],"g")),o=$):h[3]!==void 0&&(o=$):o===$?h[0]===">"?(o=s??E,u=-1):h[1]===void 0?u=-2:(u=o.lastIndex-h[2].length,d=h[1],o=h[3]===void 0?$:h[3]==='"'?ae:oe):o===ae||o===oe?o=$:o===se||o===ne?o=E:(o=$,s=void 0);const f=o===$&&r[l+1].startsWith("/>")?" ":"";n+=o===E?a+ke:u>=0?(i.push(d),a.slice(0,u)+me+a.slice(u)+g+f):a+g+(u===-2?l:f)}return[_e(r,n+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]};class O{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let n=0,o=0;const l=e.length-1,a=this.parts,[d,h]=Le(e,t);if(this.el=O.createElement(d,i),v.currentNode=this.el.content,t===2||t===3){const u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(s=v.nextNode())!==null&&a.length<l;){if(s.nodeType===1){if(s.hasAttributes())for(const u of s.getAttributeNames())if(u.endsWith(me)){const m=h[o++],f=s.getAttribute(u).split(g),k=/([.?@])?(.*)/.exec(m);a.push({type:1,index:n,name:k[2],strings:f,ctor:k[1]==="."?ze:k[1]==="?"?qe:k[1]==="@"?De:j}),s.removeAttribute(u)}else u.startsWith(g)&&(a.push({type:6,index:n}),s.removeAttribute(u));if(ge.test(s.tagName)){const u=s.textContent.split(g),m=u.length-1;if(m>0){s.textContent=H?H.emptyScript:"";for(let f=0;f<m;f++)s.append(u[f],P()),v.nextNode(),a.push({type:2,index:++n});s.append(u[m],P())}}}else if(s.nodeType===8)if(s.data===fe)a.push({type:2,index:n});else{let u=-1;for(;(u=s.data.indexOf(g,u+1))!==-1;)a.push({type:7,index:n}),u+=g.length-1}n++}}static createElement(e,t){const i=y.createElement("template");return i.innerHTML=e,i}}function S(r,e,t=r,i){if(e===w)return e;let s=i!==void 0?t._$Co?.[i]:t._$Cl;const n=N(e)?void 0:e._$litDirective$;return s?.constructor!==n&&(s?._$AO?.(!1),n===void 0?s=void 0:(s=new n(r),s._$AT(r,t,i)),i!==void 0?(t._$Co??(t._$Co=[]))[i]=s:t._$Cl=s),s!==void 0&&(e=S(r,s._$AS(r,e.values),s,i)),e}class He{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??y).importNode(t,!0);v.currentNode=s;let n=v.nextNode(),o=0,l=0,a=i[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new M(n,n.nextSibling,this,e):a.type===1?d=new a.ctor(n,a.name,a.strings,this,e):a.type===6&&(d=new je(n,this,e)),this._$AV.push(d),a=i[++l]}o!==a?.index&&(n=v.nextNode(),o++)}return v.currentNode=y,s}p(e){let t=0;for(const i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class M{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=c,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=S(this,e,t),N(e)?e===c||e==null||e===""?(this._$AH!==c&&this._$AR(),this._$AH=c):e!==this._$AH&&e!==w&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Ue(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==c&&N(this._$AH)?this._$AA.nextSibling.data=e:this.T(y.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,s=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=O.createElement(_e(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{const n=new He(s,this),o=n.u(this.options);n.p(t),this.T(o),this._$AH=n}}_$AC(e){let t=le.get(e.strings);return t===void 0&&le.set(e.strings,t=new O(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const n of e)s===t.length?t.push(i=new M(this.O(P()),this.O(P()),this,this.options)):i=t[s],i._$AI(n),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const i=ie(e).nextSibling;ie(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class j{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,n){this.type=1,this._$AH=c,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=n,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=c}_$AI(e,t=this,i,s){const n=this.strings;let o=!1;if(n===void 0)e=S(this,e,t,0),o=!N(e)||e!==this._$AH&&e!==w,o&&(this._$AH=e);else{const l=e;let a,d;for(e=n[0],a=0;a<n.length-1;a++)d=S(this,l[i+a],t,a),d===w&&(d=this._$AH[a]),o||(o=!N(d)||d!==this._$AH[a]),d===c?e=c:e!==c&&(e+=(d??"")+n[a+1]),this._$AH[a]=d}o&&!s&&this.j(e)}j(e){e===c?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class ze extends j{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===c?void 0:e}}class qe extends j{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==c)}}class De extends j{constructor(e,t,i,s,n){super(e,t,i,s,n),this.type=5}_$AI(e,t=this){if((e=S(this,e,t,0)??c)===w)return;const i=this._$AH,s=e===c&&i!==c||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,n=e!==c&&(i===c||s);s&&this.element.removeEventListener(this.name,this,i),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class je{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){S(this,e)}}const Be=C.litHtmlPolyfillSupport;Be?.(O,M),(C.litHtmlVersions??(C.litHtmlVersions=[])).push("3.3.3");const Ve=(r,e,t)=>{const i=t?.renderBefore??e;let s=i._$litPart$;if(s===void 0){const n=t?.renderBefore??null;i._$litPart$=s=new M(e.insertBefore(P(),n),n,void 0,t??{})}return s._$AI(r),s};const I=globalThis;class R extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t;const e=super.createRenderRoot();return(t=this.renderOptions).renderBefore??(t.renderBefore=e.firstChild),e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Ve(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return w}}R._$litElement$=!0,R.finalized=!0,I.litElementHydrateSupport?.({LitElement:R});const Fe=I.litElementPolyfillSupport;Fe?.({LitElement:R});(I.litElementVersions??(I.litElementVersions=[])).push("4.2.2");const We=new Set(["washing","washing_paused","clean_add_water","charging_completed","returning_to_wash","auto_emptying"]),Qe=new Set(["sweeping_and_mopping","sweeping","vacuuming","mopping","spot_cleaning","room_cleaning","segment_cleaning"]),Ge={water_tank_dry:"clean water tank empty",dirty_water_tank:"dirty water tank full",remove_mop:"remove mop pads",route:"route blocked"};function A(r){return String(r??"").trim().toLowerCase()}function $e(r){const e=A(r);return e?e.replaceAll("_"," "):""}function Ke(r){const e=A(r);return!e||e==="no_error"||e==="unknown"||e==="unavailable"?null:Ge[e]??$e(e)}function Ze(r){switch(r){case"washing":return"Washing pads";case"washing_paused":return"Washing paused";case"clean_add_water":return"Adding water";case"returning_to_wash":return"Returning to wash";case"auto_emptying":return"Auto-emptying";default:return $e(r)}}function Je(r){if(A(r.queueRunState)!=="running")return null;const e=A(r.vacuumState),t=A(r.robotState),i=A(r.taskStatus),s=Ke(r.errorCode);if(e==="error")return{phase:"error",label:s??"Error"};if(i==="completed")return{phase:"finishing",label:"Finishing step"};if(e==="paused")return{phase:"paused",label:s?`Paused (${s})`:"Paused"};if(We.has(t))return{phase:"preparing",label:Ze(t)};if(e==="returning"&&i==="room_cleaning")return{phase:"returning",label:"Returning to base"};if(Qe.has(t))switch(t){case"sweeping":case"vacuuming":return{phase:"cleaning",label:"Vacuuming"};case"mopping":return{phase:"cleaning",label:"Mopping"};case"sweeping_and_mopping":return{phase:"cleaning",label:"Vacuuming + mopping"};case"spot_cleaning":return{phase:"cleaning",label:"Spot cleaning"};default:return{phase:"cleaning",label:"Cleaning room"}}return e==="cleaning"?{phase:"cleaning",label:"Cleaning room"}:e==="returning"?{phase:"returning",label:"Returning to base"}:{phase:"unknown",label:"Working"}}function V(r,e){const t=String(r||"").trim();if(!t.startsWith("vacuum."))return null;const i=t.slice(7);return i?`sensor.${i}_${e}`:null}function z(r){return typeof r=="object"&&r!==null&&!Array.isArray(r)}function Xe(r){return String(r??"").trim()}function ve(r){return Xe(r).toLowerCase()}function U(r){return typeof r!="number"||!Number.isFinite(r)||r<0?null:Math.trunc(r)}function F(r,e){return r.filter(t=>t.status===e).length}function Ye(r){if(!z(r))return null;const e=r.item_id,t=r.room_id,i=r.room_name,s=r.status;return typeof e!="string"||typeof t!="number"||!Number.isFinite(t)||typeof i!="string"||typeof s!="string"?null:{itemId:e,roomId:t,roomName:i,status:s,overrides:z(r.overrides)?{...r.overrides}:{},result:typeof r.result=="string"?r.result:null}}function et(r){const e=ve(r);return e?e==="blocked"?"Route blocked":e==="out_of_sync"?"Out of sync":e.charAt(0).toUpperCase()+e.slice(1):"Unknown"}function tt(r){if(!z(r))return[];const e=r.queue_items;return Array.isArray(e)?e.flatMap(t=>{const i=Ye(t);return i?[i]:[]}):[]}function it(r){const e=r?.attributes,t=tt(e),i=z(e)?e:{};return{runState:ve(r?.state)||"unknown",configEntryId:typeof i.config_entry_id=="string"?i.config_entry_id:null,vacuumEntityId:typeof i.vacuum_entity_id=="string"?i.vacuum_entity_id:null,pendingItems:U(i.pending_items)??F(t,"pending"),runningItems:U(i.running_items)??F(t,"running"),completedItems:U(i.completed_items)??F(t,"completed"),totalItems:U(i.total_items)??t.length,items:t}}const ye={water_volume:[{value:0,label:"Off"},{value:1,label:"Min"},{value:2,label:"Med"},{value:3,label:"Max"}],suction_level:[{value:-1,label:"Off"},{value:0,label:"Min"},{value:1,label:"Med"},{value:2,label:"Max"},{value:3,label:"Turbo"}],repeats:[{value:1,label:"x1"},{value:2,label:"x2"},{value:3,label:"x3"}]},rt={water_volume:2,suction_level:1,repeats:1};function be(r){if(r==null)return null;if(typeof r=="number")return Number.isFinite(r)?Math.trunc(r):null;if(typeof r=="string"){const e=Number(r.trim());return Number.isFinite(e)?Math.trunc(e):null}return null}function Ae(r,e){const t={};for(const[i,s]of Object.entries(e??{}))s!=null&&(t[i]=s);for(const[i,s]of Object.entries(r??{}))s!=null&&(t[i]=s);return t}function st(r,e,t){const i=Ae(e,t);return be(i[r])??rt[r]}function nt(r,e,t){const i=st(r,e,t),s=ye[r].find(n=>n.value===i);return s?s.label:String(i)}function ot(r,e,t){const i=Ae(e,t),s=ye[r],n=be(i[r]),o=s.findIndex(a=>a.value===n),l=o<0?0:(o+1)%s.length;return i[r]=s[l].value,i}function ce(r){if(typeof r=="number"&&Number.isInteger(r))return r;if(typeof r!="string")return null;const e=r.trim();if(!e)return null;const t=Number(e);return Number.isInteger(t)?t:null}function Q(r,e){if(Array.isArray(r)){for(const n of r)Q(n,e);return}if(typeof r!="object"||r===null)return;const t=r,i=ce(t.id),s=typeof t.name=="string"?t.name.trim():"";i!==null&&s&&e.push({roomId:i,roomName:s});for(const[n,o]of Object.entries(t)){const l=ce(n);if(l!==null&&typeof o=="string"){const a=o.trim();if(a){e.push({roomId:l,roomName:a});continue}}Q(o,e)}}function at(r){const e=[];Q(r,e);const t=new Map;for(const i of e)t.set(i.roomId,i.roomName);return Array.from(t.entries()).map(([i,s])=>({roomId:i,roomName:s})).sort((i,s)=>i.roomId-s.roomId)}const q="ha-dreame-queue-card",lt="HA Dreame Queue",ct=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"},{field:"repeats",label:"Repeats"}];function ut(r,e){const t=de(e.title)||lt,i=de(e.entity)||null;if(!i)return ue({title:t,status:"not_configured",entityId:null,message:"Configure a HA Dreame queue status entity."});const s=r?.states[i];if(!s)return ue({title:t,status:"missing",entityId:i,message:"Queue entity not found."});const n=it(s),o=dt(r,n),l=ft(r,n);return{title:t,status:"ready",entityId:i,message:null,snapshot:n,activity:o,activeControls:pt(n),canClearPending:n.pendingItems>0,rooms:l,rows:ht(n.items)}}function ue({title:r,status:e,entityId:t,message:i}){return{title:r,status:e,entityId:t,message:i,snapshot:null,activity:null,activeControls:[],canClearPending:!1,rooms:[],rows:[]}}function dt(r,e){const t=e.vacuumEntityId;return!r||!t?null:Je({queueRunState:e.runState,vacuumState:T(r,t),robotState:T(r,V(t,"state")),taskStatus:T(r,V(t,"task_status")),errorCode:T(r,V(t,"error"))})}function ht(r){const e=r.flatMap((s,n)=>s.status==="pending"?[n]:[]),t=e[0]??null,i=e[e.length-1]??null;return r.map((s,n)=>({itemId:s.itemId,queuePosition:n,roomName:s.roomName,status:s.status,statusLabel:et(s.status),overrides:{...s.overrides},canRemove:s.status==="pending",canMoveUp:s.status==="pending"&&n!==t,canMoveDown:s.status==="pending"&&n!==i,overrideControls:s.status==="pending"?mt(s.overrides):[]}))}function pt(r){return r.runState==="running"?[{ariaLabel:"Cancel queue",label:"Cancel",service:"cancel_queue"},{ariaLabel:"Skip current room",label:"Skip",service:"skip_current_room"}]:r.pendingItems>0?[{ariaLabel:"Start queue",label:"Start",service:"start_queue"}]:[]}function mt(r){return ct.map(e=>({field:e.field,label:e.label,valueLabel:nt(e.field,r,{})}))}function ft(r,e){const t=e.vacuumEntityId;if(!r||!t)return[];const i=r.states[t]?.attributes;return at(gt(i)?i.rooms:void 0)}function T(r,e){return e?r.states[e]?.state:void 0}function de(r){return String(r??"").trim()}function gt(r){return typeof r=="object"&&r!==null&&!Array.isArray(r)}const D=class D extends R{constructor(){super(...arguments),this._config={}}setConfig(e){if(!e||typeof e!="object")throw new Error("Invalid HA Dreame queue card configuration");this._config={...e}}getCardSize(){return 3}render(){const e=ut(this.hass,this._config),t=e.snapshot;return p`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${e.title}</h2>
            <p class="subtitle">${e.activity?.label??e.entityId??"Read-only queue"}</p>
          </div>
          ${t?p`<span class="state-pill ${t.runState}"
                >${this._stateLabel(t.runState)}</span
              >`:c}
        </div>

        ${e.message?p`<div class="message">${e.message}</div>`:p`
              <div class="counts">
                ${this._count("Pending",t?.pendingItems??0)}
                ${this._count("Running",t?.runningItems??0)}
                ${this._count("Done",t?.completedItems??0)}
                ${this._count("Total",t?.totalItems??0)}
              </div>
              ${e.activeControls.length||e.canClearPending?p`
                    <div class="queue-actions">
                      ${e.activeControls.map(i=>p`
                          <button
                            aria-label=${i.ariaLabel}
                            class="row-action"
                            type="button"
                            ?disabled=${!t?.configEntryId}
                            @click=${()=>this._callQueueService(t?.configEntryId,i.service)}
                          >
                            ${i.label}
                          </button>
                        `)}
                      ${e.canClearPending?p`
                            <button
                              aria-label="Clear pending queue"
                              class="row-action"
                              type="button"
                              ?disabled=${!t?.configEntryId}
                              @click=${()=>this._clearPending(t?.configEntryId)}
                            >
                              Clear pending
                            </button>
                          `:c}
                    </div>
                  `:c}
              <div class="queue-list">
                ${e.rows.length?e.rows.map(i=>p`
                        <div class="queue-row">
                          <span class="room-name">${i.roomName}</span>
                          <div class="row-actions">
                            <span class="row-status">${i.statusLabel}</span>
                            ${i.overrideControls.map(s=>p`
                                <button
                                  aria-label=${`Cycle ${i.roomName} ${this._overrideAriaField(s.field)}`}
                                  class="row-action"
                                  type="button"
                                  ?disabled=${!t?.configEntryId}
                                  @click=${()=>this._updateOverrides(t?.configEntryId,i.itemId,s.field,i.overrides)}
                                >
                                  ${s.label} ${s.valueLabel}
                                </button>
                              `)}
                            ${i.canMoveUp?p`
                                  <button
                                    aria-label=${`Move ${i.roomName} up`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._moveItem(t?.configEntryId,i.itemId,i.queuePosition-1)}
                                  >
                                    Up
                                  </button>
                                `:c}
                            ${i.canMoveDown?p`
                                  <button
                                    aria-label=${`Move ${i.roomName} down`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._moveItem(t?.configEntryId,i.itemId,i.queuePosition+1)}
                                  >
                                    Down
                                  </button>
                                `:c}
                            ${i.canRemove?p`
                                  <button
                                    aria-label=${`Remove ${i.roomName}`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._removeItem(t?.configEntryId,i.itemId)}
                                  >
                                    Remove
                                  </button>
                                `:c}
                          </div>
                        </div>
                      `):p`<div class="message">Queue is empty.</div>`}
              </div>
              ${e.rooms.length?p`
                    <div class="section-title">Available rooms</div>
                    <div class="room-catalog">
                      ${e.rooms.map(i=>p`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!t?.configEntryId}
                            @click=${()=>this._addRoom(t?.configEntryId,i.roomId,i.roomName)}
                          >
                            ${i.roomName}
                          </button>
                        `)}
                    </div>
                  `:c}
            `}
      </ha-card>
    `}_count(e,t){return p`
      <div class="count">
        <span class="count-value">${t}</span>
        <span class="count-label">${e}</span>
      </div>
    `}_stateLabel(e){return e.split("_").filter(t=>t.length>0).map(t=>t.charAt(0).toUpperCase()+t.slice(1)).join(" ")}_addRoom(e,t,i){!e||!this.hass?.callService||this.hass.callService("ha_dreame","add_queue_room",{config_entry_id:e,room_id:t,room_name:i})}_removeItem(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame","remove_queue_item",{config_entry_id:e,item_id:t})}_moveItem(e,t,i){!e||!this.hass?.callService||this.hass.callService("ha_dreame","move_queue_item",{config_entry_id:e,item_id:t,new_position:i})}_clearPending(e){!e||!this.hass?.callService||this.hass.callService("ha_dreame","clear_pending_queue",{config_entry_id:e})}_callQueueService(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame",t,{config_entry_id:e})}_updateOverrides(e,t,i,s){!e||!this.hass?.callService||this.hass.callService("ha_dreame","update_queue_item_overrides",{config_entry_id:e,item_id:t,overrides:ot(i,s,{})})}_overrideAriaField(e){return e==="water_volume"?"water volume":e==="suction_level"?"suction level":"repeats"}};D.properties={hass:{attribute:!1},_config:{state:!0}},D.styles=Se`
    :host {
      display: block;
    }

    ha-card {
      display: block;
      padding: 14px;
    }

    .header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: start;
      gap: 10px;
      margin-bottom: 12px;
    }

    .title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .subtitle {
      margin: 3px 0 0;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .state-pill {
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.2;
      padding: 4px 9px;
      white-space: nowrap;
    }

    .state-pill.running {
      border-color: var(--state-active-color, #2e7d32);
      color: var(--state-active-color, #2e7d32);
    }

    .state-pill.blocked,
    .state-pill.out_of_sync,
    .state-pill.error {
      border-color: var(--error-color, #d32f2f);
      color: var(--error-color, #d32f2f);
    }

    .message {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      color: var(--secondary-text-color);
      font-size: 0.86rem;
      line-height: 1.35;
      padding: 10px;
    }

    .counts {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 8px;
    }

    .count {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      min-width: 0;
      padding: 7px 8px;
    }

    .count-value {
      display: block;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.1;
    }

    .count-label {
      color: var(--secondary-text-color);
      display: block;
      font-size: 0.72rem;
      line-height: 1.2;
      margin-top: 3px;
      overflow-wrap: anywhere;
    }

    .queue-list {
      display: grid;
      gap: 6px;
    }

    .queue-actions {
      display: flex;
      justify-content: flex-end;
      margin: 0 0 12px;
    }

    .section-title {
      color: var(--secondary-text-color);
      font-size: 0.74rem;
      font-weight: 600;
      line-height: 1.2;
      margin: 12px 0 6px;
      text-transform: uppercase;
    }

    .room-catalog {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .room-chip {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.78rem;
      line-height: 1.2;
      max-width: 100%;
      overflow: hidden;
      padding: 5px 9px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .room-chip:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }

    .queue-row {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      display: grid;
      gap: 8px;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      min-height: 34px;
      padding: 7px 9px;
    }

    .room-name {
      font-size: 0.88rem;
      font-weight: 600;
      line-height: 1.25;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .row-status {
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      white-space: nowrap;
    }

    .row-actions {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      justify-content: flex-end;
    }

    .row-action {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.74rem;
      line-height: 1.2;
      padding: 3px 8px;
      white-space: nowrap;
    }

    .row-action:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }
  `;let G=D;customElements.get(q)||customElements.define(q,G);window.customCards=window.customCards??[];window.customCards.some(r=>r.type===q)||window.customCards.push({type:q,name:"HA Dreame Queue",description:"Read-only queue summary for HA Dreame."});

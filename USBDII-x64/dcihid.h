#ifndef _DCIHID_H_
#define _DCIHID_H_

#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


/*
 * function prototypes
 */
u_int32_t dcihid_open(const char *dev_name, const u_int card_id, const u_int card_num);
int32_t   dcihid_close(const u_int32_t dcihid_handle);
int32_t   dcihid_write(const u_int32_t dcihid_handle, const u_int32_t addr, const u_int32_t data);
int32_t   dcihid_read(const u_int32_t dcihid_handle, const u_int32_t addr, u_int8_t *data);

#ifdef _cplusplus
}
#endif /* _cplusplus */

#endif /* _DCIHID_H_ */
